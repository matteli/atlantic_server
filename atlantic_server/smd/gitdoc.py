from time import time

# pylint: disable=no-name-in-module
from pygit2 import (
    init_repository,
    Repository,
    Signature,
    GIT_FILEMODE_BLOB,
)


def init_repo(repo_name):
    init_repository("doc/" + repo_name, bare=True)
    repo = Repo(repo_name)
    return repo


class Repo(Repository):
    def __init__(self, repo_name):
        super().__init__("doc/" + repo_name)

    def _get_tree(self, branch_name):
        commit = self._get_commit(branch_name)
        if commit:
            return commit.tree
        return None

    def _get_commit(self, branch_name):
        branch = self.branches.get(branch_name)
        if branch:
            commit_id = branch.target
            commit = self.get(commit_id)
            return commit
        return None

    def _get_blob_by_name(self, branch_name, filename):
        tree = self._get_tree(branch_name)
        if filename in tree:
            blob = tree[filename]
            return blob
        return None

    def commit_file(
        self,
        filename,
        content,
        author,
        email,
        branch_name="master",
        message="",
        timezone=0,
        first_commit=False,
        parent_commit_id=0,
    ):
        if not first_commit:
            if parent_commit_id:
                parent_commit = self.get(parent_commit_id)
            else:
                parent_commit = self._get_commit(branch_name)
            parents = [parent_commit.id]
            tree_parent = parent_commit.tree_id
            tree_builder = self.TreeBuilder(tree_parent)
        else:
            parents = []
            tree_builder = self.TreeBuilder()
        blob_id = self.create_blob(content.encode(encoding="UTF-8"))
        tree_builder.insert(filename, blob_id, GIT_FILEMODE_BLOB)
        tree = tree_builder.write()
        author = committer = Signature(author, email, int(time()), timezone)
        commit_id = self.create_commit(
            "refs/heads/" + branch_name, author, committer, message, tree, parents
        )
        if commit_id:
            return {"commit_id": str(commit_id), "blob_id": str(blob_id)}
        return {"commit_id": "", "blob_id": ""}

    def list_branches(self):
        return list(self.branches)

    def branch_exist(self, branch):
        branch = self.branches.get(branch)
        if branch:
            return True
        return False

    def file_exist(self, branch_name, filename):
        tree = self._get_tree(branch_name)
        return filename in tree

    def list_files(self, branch_name):
        files = {}
        tree = self._get_tree(branch_name)
        if tree:
            for obj in tree:
                files[str(obj.id)] = {"filename": obj.name}
        return files

    def get_file(self, branch_name, filename):
        commit = self._get_commit(branch_name)
        if commit:
            tree = commit.tree
            if filename in tree:
                blob = tree[filename]
                if blob:
                    return {
                        "commit": str(commit.id),
                        "xml_str": blob.data.decode(encoding="UTF-8"),
                    }
        return {}

    def get_file_by_id(self, blob_id):
        blob = self.get(blob_id)
        return blob.data.decode(encoding="UTF-8")
