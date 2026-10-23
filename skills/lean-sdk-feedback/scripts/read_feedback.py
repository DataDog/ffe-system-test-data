#!/usr/bin/env python3
"""Read a complete GitHub feedback snapshot; never mutate GitHub state."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess


def gh(*args):
    return json.loads(subprocess.check_output(['gh', 'api', *args], text=True))


def pages(endpoint):
    return [item for page in gh('--paginate', '--slurp', endpoint + '?per_page=100') for item in page]


def graphql(query, **variables):
    result = gh('graphql', '-f', 'query=' + query, *[
        arg for key, value in variables.items() if value is not None
        for arg in ('-F' if isinstance(value, int) else '-f', f'{key}={value}')])
    if result.get('errors'):
        raise ValueError(result['errors'])
    return result['data']


THREADS = '''query($owner:String!,$name:String!,$number:Int!,$cursor:String) {
  repository(owner:$owner,name:$name) { pullRequest(number:$number) {
    reviewDecision reviewThreads(first:100,after:$cursor) {
      pageInfo {hasNextPage endCursor}
      nodes {id isResolved isOutdated path line
        comments(first:100) {pageInfo {hasNextPage endCursor} nodes {databaseId}}}
    }
  }}
}'''
COMMENTS = '''query($id:ID!,$cursor:String) {
  node(id:$id) { ... on PullRequestReviewThread {
    comments(first:100,after:$cursor) {pageInfo {hasNextPage endCursor} nodes {databaseId}}
  }}
}'''


def read_pr(repo, number):
    endpoint = f'repos/{repo}/pulls/{number}'
    before = gh(endpoint)
    owner, name = repo.split('/')
    cursor, threads = None, []
    while True:
        pr = graphql(THREADS, owner=owner, name=name, number=number, cursor=cursor)['repository']['pullRequest']
        batch = pr['reviewThreads']
        for thread in batch['nodes']:
            comments = thread.pop('comments')
            ids = [c['databaseId'] for c in comments['nodes']]
            while comments['pageInfo']['hasNextPage']:
                comments = graphql(COMMENTS, id=thread['id'], cursor=comments['pageInfo']['endCursor'])['node']['comments']
                ids.extend(c['databaseId'] for c in comments['nodes'])
            thread['comment_ids'] = ids
            threads.append(thread)
        if not batch['pageInfo']['hasNextPage']:
            break
        cursor = batch['pageInfo']['endCursor']
    inline = pages(endpoint + '/comments')
    if {i for t in threads for i in t['comment_ids']} != {c['id'] for c in inline}:
        raise ValueError('Thread/inline inventory changed or is incomplete; refresh the snapshot')
    fields = ('id', 'html_url', 'body', 'created_at', 'updated_at', 'submitted_at',
              'state', 'commit_id', 'original_commit_id', 'path', 'line', 'original_line',
              'in_reply_to_id', 'pull_request_review_id', 'diff_hunk')
    def normalize(items):
        return [{**{k: item[k] for k in fields if k in item},
                 'author': (item.get('user') or {}).get('login')} for item in items]
    result = {
        'repository': repo, 'number': number, 'url': before['html_url'],
        'title': before['title'], 'body': before['body'], 'state': before['state'],
        'draft': before['draft'], 'head_sha': before['head']['sha'],
        'base_sha': before['base']['sha'], 'head_ref': before['head']['ref'],
        'base_ref': before['base']['ref'], 'review_decision': pr['reviewDecision'],
        'threads': threads, 'inline_comments': normalize(inline),
        'conversation_comments': normalize(pages(f'repos/{repo}/issues/{number}/comments')),
        'reviews': normalize(pages(endpoint + '/reviews')),
    }
    check_pages = gh('--paginate', '--slurp',
                     f'repos/{repo}/commits/{result["head_sha"]}/check-runs?per_page=100')
    result['check_runs'] = [{k: c.get(k) for k in
                            ('name', 'status', 'conclusion', 'head_sha', 'details_url', 'started_at', 'completed_at')}
                           for page in check_pages for c in page['check_runs']]
    result['commit_statuses'] = [{k: c.get(k) for k in
                                 ('context', 'state', 'target_url', 'created_at', 'updated_at')}
                                for c in pages(f'repos/{repo}/commits/{result["head_sha"]}/statuses')]
    after = gh(endpoint)
    if any(before[k]['sha'] != after[k]['sha'] for k in ('head', 'base')):
        raise ValueError('PR head/base moved during collection; refresh the snapshot')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository')
    parser.add_argument('pull_requests', nargs='+', type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repository):
        parser.error('repository must be OWNER/REPO')
    if any(n <= 0 for n in args.pull_requests) or len(set(args.pull_requests)) != len(args.pull_requests):
        parser.error('PR numbers must be positive and unique')
    result = {'schema_version': 1, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
              'pull_requests': [read_pr(args.repository, n) for n in args.pull_requests]}
    # Recheck earlier parents after collecting later children too.
    for pr in result['pull_requests']:
        current = gh(f'repos/{args.repository}/pulls/{pr["number"]}')
        if current['head']['sha'] != pr['head_sha'] or current['base']['sha'] != pr['base_sha']:
            raise ValueError('Stack head/base moved during collection; refresh the snapshot')
    result['completed_at'] = datetime.now(timezone.utc).isoformat()
    result['consistency_limit'] = ('Heads and bases rechecked after collection; GitHub discussions, '
                                   'thread state and checks are nontransactional reads over this window. '
                                   'Refresh before acting on review state.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({p['number']: {'head': p['head_sha'], 'threads': len(p['threads']),
                      'inline_comments': len(p['inline_comments']), 'review_decision': p['review_decision']}
                      for p in result['pull_requests']}, indent=2))


if __name__ == '__main__':
    main()
