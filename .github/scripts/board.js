// Keeps the project board in sync with issues and pull requests, so nobody has
// to drag cards by hand. Run by .github/workflows/board.yml.
//
// Two kinds of cards, told apart by label:
//   take-home  a personal card, made from a "Take-home N" issue template
//   task       a shared club task, claimed by commenting /claim
//
// How cards move:
//   take-home card created, or /claim       -> In progress
//   pull request says "Closes #N"           -> In review
//   issue closed (merged PR or by hand)     -> Done
//   /unclaim, last person leaves            -> To do
//
// GitHub's built-in Actions token can't edit organization projects, so moving
// cards needs a PROJECT_TOKEN secret (see CONTRIBUTING.md, "For leads").
// Without it, assigning people and replying to comments still works.

const ORG = 'data-science-ucsb';
const PROJECT_NUMBER = 11;
const BOARD_URL = `https://github.com/orgs/${ORG}/projects/${PROJECT_NUMBER}`;
const MY_CARDS_URL = `${BOARD_URL}/views/2`;
const ROADMAP_URL = 'https://github.com/data-science-ucsb/sports-stats-explorer/blob/main/ROADMAP.md';

const TODO = 'To do';
const IN_PROGRESS = 'In progress';
const IN_REVIEW = 'In review';
const DONE = 'Done';

const PERSONAL = 'take-home';
const SHARED = 'task';
const GROUP = 'after-workshops'; // several people may claim these
const MAX_ASSIGNEES = 10; // GitHub's limit per issue

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const labelNames = (issue) => issue.labels.map((l) => (typeof l === 'string' ? l : l.name));
const hasLabel = (issue, name) => labelNames(issue).includes(name);
const isTracked = (issue) => hasLabel(issue, PERSONAL) || hasLabel(issue, SHARED);
const mentionAll = (logins) => logins.map((l) => `@${l}`).join(', ');

module.exports = async ({ github, context, core }) => {
  const { owner, repo } = context.repo;
  const board = await openBoard(core);

  const reply = (number, lines) =>
    github.rest.issues.createComment({ owner, repo, issue_number: number, body: [].concat(lines).join('\n') });

  // Moves a card. `from` limits which columns it may move out of (null = no column yet).
  // Returns true if the card is now in `status`.
  async function move(issue, status, { from } = {}) {
    if (!board) return false;
    try {
      return await board.setStatus(issue, status, from);
    } catch (error) {
      core.setFailed(`Couldn't move #${issue.number} to ${status}: ${error.message}`);
      return false;
    }
  }

  async function assign(number, login) {
    const { data } = await github.rest.issues.addAssignees({ owner, repo, issue_number: number, assignees: [login] });
    const ok = data.assignees.some((a) => a.login === login);
    if (!ok) core.warning(`GitHub didn't let @${login} be assigned to #${number}.`);
    return ok;
  }

  // ---- issues ---------------------------------------------------------------

  async function onIssue(action, issue) {
    if (!isTracked(issue)) return;
    const assigned = issue.assignees.length > 0;

    switch (action) {
      case 'opened':
        if (hasLabel(issue, PERSONAL)) return startPersonalCard(issue);
        return move(issue, assigned ? IN_PROGRESS : TODO);

      case 'labeled': {
        // A card label added later puts an existing issue on the board. Labels from
        // a template also fire this right after 'opened', which already handled them.
        const added = context.payload.label.name;
        const ageMs = Date.now() - Date.parse(issue.created_at);
        if (![PERSONAL, SHARED].includes(added) || ageMs < 60_000 || issue.state !== 'open') return;
        return move(issue, assigned ? IN_PROGRESS : TODO, { from: [null] });
      }

      case 'assigned': // a lead assigned someone by hand
        return move(issue, IN_PROGRESS, { from: [null, TODO] });

      case 'unassigned':
        if (!assigned) return move(issue, TODO, { from: [IN_PROGRESS] });
        return;

      case 'closed':
        return move(issue, DONE);

      case 'reopened':
        return move(issue, assigned || hasLabel(issue, PERSONAL) ? IN_PROGRESS : TODO);
    }
  }

  async function startPersonalCard(issue) {
    const author = issue.user.login;

    // Catch a double-clicked "Create" button.
    const mine = await github.paginate(github.rest.issues.listForRepo, {
      owner, repo, creator: author, labels: PERSONAL, state: 'open', per_page: 100,
    });
    const twin = mine.find((i) => i.number < issue.number && i.title === issue.title);
    if (twin) {
      await reply(issue.number, [
        `Hi @${author}, you already have a card for this one: #${twin.number}. ` +
          `I've closed this copy so your board stays tidy. Keep using #${twin.number}!`,
      ]);
      await github.rest.issues.update({ owner, repo, issue_number: issue.number, state: 'closed', state_reason: 'not_planned' });
      return;
    }

    await assign(issue.number, author);
    const moved = await move(issue, IN_PROGRESS);
    await reply(issue.number, [
      `👋 Hi @${author}! This is your own card` +
        (moved ? `, and it's in **In progress** on the [board](${MY_CARDS_URL}).` : '.'),
      '',
      '- Tick the boxes above as you finish each step.',
      `- Opening a pull request for this? Put \`Closes #${issue.number}\` in its description and this card moves along by itself.`,
      '- Finished without a pull request? Click **Close issue** at the bottom of this page.',
      '',
      'Stuck for more than 20 minutes? Post in the club channel. Everyone gets stuck!',
    ]);
  }

  // ---- /claim and /unclaim ----------------------------------------------------

  async function onComment(comment, issue) {
    if (issue.pull_request || comment.user.type === 'Bot') return;
    const command = comment.body.trim().split(/\s+/)[0].toLowerCase();
    if (command !== '/claim' && command !== '/unclaim') return;

    const user = comment.user.login;
    const n = issue.number;
    const assignees = issue.assignees.map((a) => a.login);

    if (hasLabel(issue, PERSONAL)) {
      return reply(n, user === issue.user.login
        ? `@${user} this is your own take-home card, so it's already yours. No need to claim it!`
        : `@${user} this is @${issue.user.login}'s own take-home card. To make yours, click **Start your card** under that take-home in [ROADMAP.md](${ROADMAP_URL}).`);
    }
    if (!hasLabel(issue, SHARED)) {
      return reply(n, `@${user} only cards labeled \`task\` can be claimed. Find one in the **To do** column on the [board](${BOARD_URL}).`);
    }
    if (issue.state === 'closed') {
      return reply(n, `@${user} this card is already done. Pick another one from the **To do** column on the [board](${BOARD_URL}).`);
    }

    if (command === '/claim') {
      if (assignees.includes(user)) {
        return reply(n, `@${user} you've already claimed this one. Go for it!`);
      }
      const isGroup = hasLabel(issue, GROUP);
      if (assignees.length > 0 && !isGroup) {
        return reply(n, `@${user} ${mentionAll(assignees)} already claimed this card. ` +
          `Ask in a comment here if you'd like to team up, or pick another card from the **To do** column on the [board](${BOARD_URL}).`);
      }
      if (assignees.length >= MAX_ASSIGNEES) {
        return reply(n, `@${user} this card already has ${MAX_ASSIGNEES} people, which is GitHub's limit. Ask a lead about splitting it into smaller cards.`);
      }
      if (!(await assign(n, user))) {
        return reply(n, `@${user} sorry, GitHub wouldn't let me assign you. A lead will sort it out. (Leads: see the "board" workflow log.)`);
      }
      const moved = await move(issue, IN_PROGRESS, { from: [null, TODO] });
      return reply(n, [
        `✅ @${user} this card is yours!` + (moved ? ` It's now in **In progress** on the [board](${MY_CARDS_URL}).` : ''),
        ...(isGroup && assignees.length ? ['', `You're joining ${mentionAll(assignees)}. Say hi!`] : []),
        '',
        '**Next steps**',
        `1. Make a branch for it: \`git checkout -b issue-${n}\``,
        `2. When you open your pull request, put \`Closes #${n}\` in its description. The card moves to **In review** by itself.`,
        '',
        'Changed your mind? Comment `/unclaim` and the card goes back to **To do** for someone else.',
      ]);
    }

    // /unclaim
    if (!assignees.includes(user)) {
      return reply(n, `@${user} you haven't claimed this card, so there's nothing to undo.`);
    }
    await github.rest.issues.removeAssignees({ owner, repo, issue_number: n, assignees: [user] });
    const moved = assignees.length === 1 && (await move(issue, TODO, { from: [IN_PROGRESS] }));
    return reply(n, `@${user} done, you're off this card` +
      (moved ? ` and it's back in **To do** for someone else.` : '.') + ' Thanks for letting everyone know!');
  }

  // ---- pull requests ----------------------------------------------------------

  async function onPullRequest(action, pr) {
    if (action !== 'closed' && pr.state === 'closed') return; // e.g. editing an old pull request
    // GitHub links "Closes #N" a moment after the pull request is created.
    if (action === 'opened') await sleep(5000);
    const issues = (await linkedIssues(pr.number)).filter((i) => i.state === 'open' && isTracked(i));

    if (action !== 'closed') {
      for (const issue of issues) await move(issue, IN_REVIEW, { from: [null, TODO, IN_PROGRESS] });
      return;
    }
    if (pr.merged) return; // the merge closes the issues, and 'closed' moves them to Done

    const closedByAuthor = context.payload.sender.login === pr.user.login;
    for (const issue of issues) {
      if (hasLabel(issue, PERSONAL) && issue.user.login === pr.user.login && !closedByAuthor) {
        // Take-homes are practice: leads merge one version and close the rest after giving feedback.
        await reply(issue.number, [
          `🎉 @${issue.user.login} a lead reviewed and closed your pull request #${pr.number}, so this card is done. Nice work!`,
          '',
          'Check the pull request for their feedback. Still working on it? Click **Reopen issue** below.',
        ]);
        await github.rest.issues.update({ owner, repo, issue_number: issue.number, state: 'closed', state_reason: 'completed' });
        await move(issue, DONE);
      } else {
        const back = issue.assignees.length || hasLabel(issue, PERSONAL) ? IN_PROGRESS : TODO;
        await move(issue, back, { from: [IN_REVIEW] });
        await reply(issue.number, `Pull request #${pr.number} was closed without merging, so this card is back in **${back}**.` +
          (hasLabel(issue, SHARED) ? ' Keep going, or comment `/unclaim` to free it up for someone else.' : ''));
      }
    }
  }

  async function linkedIssues(number) {
    const data = await github.graphql(`
      query($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $number) {
            closingIssuesReferences(first: 10) {
              nodes {
                id number state
                author { login }
                repository { nameWithOwner }
                labels(first: 20) { nodes { name } }
                assignees(first: 10) { nodes { login } }
              }
            }
          }
        }
      }`, { owner, repo, number });
    return data.repository.pullRequest.closingIssuesReferences.nodes
      .filter((i) => i.repository.nameWithOwner === `${owner}/${repo}`)
      .map((i) => ({
        node_id: i.id,
        number: i.number,
        state: i.state.toLowerCase(),
        user: { login: i.author?.login },
        labels: i.labels.nodes,
        assignees: i.assignees.nodes,
      }));
  }

  // ---- dispatch ---------------------------------------------------------------

  const { payload } = context;
  switch (context.eventName) {
    case 'issues':
      return onIssue(payload.action, payload.issue);
    case 'issue_comment':
      return onComment(payload.comment, payload.issue);
    case 'pull_request_target':
      return onPullRequest(payload.action, payload.pull_request);
  }
};

// Reads the project once per run. Returns null (and warns) if there is no usable token.
async function openBoard(core) {
  const token = process.env.PROJECT_TOKEN;
  if (!token) {
    core.warning('No PROJECT_TOKEN secret, so cards will not move on the board. See CONTRIBUTING.md, "For leads".');
    return null;
  }
  // github-script doesn't hand out a second client, so call the GraphQL API directly.
  const graphql = async (query, variables) => {
    const response = await fetch('https://api.github.com/graphql', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, variables }),
    });
    const body = await response.json();
    if (!response.ok || body.errors) {
      throw new Error(body.errors?.map((e) => e.message).join('; ') ?? `${response.status} ${response.statusText}`);
    }
    return body.data;
  };

  let project;
  try {
    ({ organization: { projectV2: project } } = await graphql(`
      query($org: String!, $number: Int!) {
        organization(login: $org) {
          projectV2(number: $number) {
            id
            field(name: "Status") { ... on ProjectV2SingleSelectField { id options { id name } } }
          }
        }
      }`, { org: ORG, number: PROJECT_NUMBER }));
  } catch (error) {
    core.setFailed(`PROJECT_TOKEN can't read the board (expired?): ${error.message}`);
    return null;
  }

  return {
    // Adds the issue to the board if needed, then sets its column.
    async setStatus(issue, status, from) {
      const { addProjectV2ItemById: { item } } = await graphql(`
        mutation($project: ID!, $content: ID!) {
          addProjectV2ItemById(input: { projectId: $project, contentId: $content }) {
            item { id status: fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } } }
          }
        }`, { project: project.id, content: issue.node_id });

      const current = item.status?.name ?? null;
      if (current === status) return true;
      if (from && !from.includes(current)) {
        core.info(`#${issue.number}: left in ${current} (not moving to ${status})`);
        return false;
      }
      const option = project.field.options.find((o) => o.name === status);
      if (!option) throw new Error(`the board has no "${status}" column`);

      await graphql(`
        mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $project, itemId: $item, fieldId: $field, value: { singleSelectOptionId: $option }
          }) { clientMutationId }
        }`, { project: project.id, item: item.id, field: project.field.id, option: option.id });
      core.info(`#${issue.number}: ${current ?? 'not on board'} -> ${status}`);
      return true;
    },
  };
}
