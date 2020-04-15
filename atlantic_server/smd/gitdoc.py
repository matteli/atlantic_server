from time import time

from pygit2 import init_repository, Repository, Signature, GIT_FILEMODE_BLOB


def init_repo(reponame):
    repo = init_repository("doc/" + reponame, bare=True)
    return repo


def commit_file(
    repo_name,
    filename,
    content,
    author,
    email,
    branch_name="all",
    message="",
    tz=0,
    first_commit=False,
):
    repo = Repository("doc/" + repo_name)
    if not first_commit:
        ref = repo.references["refs/heads/" + branch_name]
        parent_commmit = repo.get(ref.target)
        parents = [parent_commmit.id]
        tree_parent = parent_commmit.tree_id
        tree_builder = repo.TreeBuilder(tree_parent)
        # if tree_builder.get(filename):
        #    tree_builder.remove(filename)
    else:
        parents = []
        tree_builder = repo.TreeBuilder()
    blob = repo.create_blob(content.encode(encoding="UTF-8"))
    tree_builder.insert(filename, blob, GIT_FILEMODE_BLOB)
    tree = tree_builder.write()
    author = committer = Signature(author, email, int(time()), tz)
    repo.create_commit(
        "refs/heads/" + branch_name, author, committer, message, tree, parents
    )
    if blob:
        return str(blob)
    else:
        return None


def list_branches(repo_name):
    repo = Repository("doc/" + repo_name)
    return list(repo.branches)


def branch_exist(repo_name, branch):
    repo = Repository("doc/" + repo_name)
    b = repo.branches.get(branch)
    if b:
        return b.branch_name
    else:
        return None


def get_tree(repo_name, branch_name):
    repo = Repository("doc/" + repo_name)
    branch = repo.branches.get(branch_name)
    if branch:
        btarget = branch.target
        commit = repo.get(btarget)
        return commit.tree
    return None


def list_files(repo_name, branch_name):
    files = []
    tree = get_tree(repo_name, branch_name)
    if tree:
        for obj in tree:
            files.append({"hash": str(obj.id), "filename": obj.name})
    return files


def get_content_by_name(repo_name, branch_name, filename):
    tree = get_tree(repo_name, branch_name)
    if filename in tree:
        blob = tree[filename]
        return blob.data.decode(encoding="UTF-8")
    return None


def get_content_by_hash(repo_name, blobhash):
    repo = Repository("doc/" + repo_name)
    blob = repo.get(blobhash)
    return blob.data.decode(encoding="UTF-8")
