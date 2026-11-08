"""Approved scratch allowance; explicit test/config/dependency exclusions."""
import ast
from pathlib import PurePosixPath

from . import partb as b

PROTECTED_DIRECTORIES={'test','tests','testing','__tests__','config','configs','configuration','settings',
    '.config','.github','.gitlab','.circleci','requirements','dependencies','deps','vendor','third_party',
    'third-party','node_modules','site-packages','.venv','venv','.git','handoff_refs'}
PROTECTED_NAMES={'conftest.py','pytest_plugins.py','setup.py','setup.cfg','pyproject.toml','tox.ini','pytest.ini','config',
    '.coveragerc','pylintrc','.pylintrc','.envrc','pipfile','pipfile.lock','poetry.lock','uv.lock',
    'package.json','package-lock.json','npm-shrinkwrap.json','yarn.lock','pnpm-lock.yaml',
    'environment.yml','environment.yaml','dockerfile','makefile','manifest.in','config.py','settings.py',
    '.gitignore','.gitattributes','.gitmodules','.editorconfig','.dockerignore','.npmrc','.pypirc',
    '.python-version','.tool-versions','.config'}
CONFIG_SUFFIXES={'.toml','.ini','.cfg','.conf','.config','.yaml','.yml','.lock','.whl','.egg'}


def protected_path(name,record):
    """Frozen conventions, not an inference about an arbitrary file's intent."""
    path=PurePosixPath(name);parts=[v.lower() for v in path.parts];base=parts[-1]
    if any(v in PROTECTED_DIRECTORIES for v in parts[:-1]):return True
    if base in PROTECTED_NAMES or path.suffix.lower() in CONFIG_SUFFIXES:return True
    if base.startswith(('config.','settings.','configuration.')):return True
    if base=='.env' or base.startswith('.env.') or base.startswith(('requirements','constraints','dockerfile.')):return True
    if ('requirements' in base or 'constraints' in base) and path.suffix.lower() in {'.txt','.in'}:return True
    if base.endswith(('.config.js','.config.cjs','.config.mjs','.config.json','.config.py','_config.py')):return True
    if path.suffix.lower() in {'.py','.sh'} and (base.startswith('test_') or base.endswith(('_test.py','_test.sh')) or base in {'test.py','tests.py','test.sh'}):return True
    if path.suffix.lower()=='.py' and record.get('kind')=='file':
        try:tree=ast.parse(b.contents(record).decode('utf-8'))
        except (SyntaxError,UnicodeError):return False
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_'):return True
            if isinstance(node,ast.ClassDef) and node.name.startswith('Test'):return True
            if isinstance(node,ast.Import) and any(v.name.split('.')[0] in {'pytest','unittest'} for v in node.names):return True
            if isinstance(node,ast.ImportFrom) and node.module and node.module.split('.')[0] in {'pytest','unittest'}:return True
    return False


def separate_scratch(baseline,final):
    def allowed(name,record):
        parts=PurePosixPath(name).parts
        if not b.safe_relative(name):raise ValueError('unsafe recorded path')
        if record.get('kind')!='file' or parts[0]=='radon' or protected_path(name,record):return False
        # Existing non-scratch repository files retain their original policy.
        return name not in baseline or (len(parts)>1 and parts[0]=='.scratch')
    left={p:r for p,r in baseline.items() if not allowed(p,r)}
    right={p:r for p,r in final.items() if not allowed(p,r)}
    inventory={'baseline':{p:r for p,r in baseline.items() if allowed(p,r)},
               'final':{p:r for p,r in final.items() if allowed(p,r)}}
    # A regular scratch file replaced by a symlink must still be rejected.
    for p in set(baseline)|set(final):
        if p in baseline and p in final and baseline[p]['kind']!=final[p]['kind']:
            left[p]=baseline[p];right[p]=final[p]
    return left,right,inventory


def describe_scratch(inventory):
    result=[]
    for name in sorted(set(inventory['baseline'])|set(inventory['final'])):
        before=inventory['baseline'].get(name);after=inventory['final'].get(name)
        item={'path':name,'change':'created' if before is None else 'deleted' if after is None else 'unchanged' if before==after else 'modified'}
        for label,record in [('before',before),('after',after)]:
            item[label]=None if record is None else {'sha256':record['sha256'],'bytes':len(b.contents(record)),'mode':record['mode']}
        result.append(item)
    return result


def excluded_policy_violations(metadata):
    """Audit protected changes in otherwise excluded cache/Git metadata."""
    if not metadata:return []
    before=metadata['baseline'];after=metadata['final'];violations=[]
    for name in sorted(set(before)|set(after)):
        a=before.get(name);z=after.get(name)
        if a==z:continue
        parts=PurePosixPath(name).parts
        if (a and a['kind']=='symlink') or (z and z['kind']=='symlink'):
            reason='symlink_in_excluded_metadata'
        elif parts[0]=='.git':
            if len(parts)<2 or (parts[1]!='config' and parts[1]!='hooks'):continue
            reason='git_config_or_hook_change'
        else:
            # Framework cache marker files are runtime metadata. A test,
            # config or dependency file placed in a cache is not exempt.
            if '.pytest_cache' in parts and parts[-1] in {'.gitignore','CACHEDIR.TAG','README.md'}:continue
            logical='/'.join(v for v in parts if v not in b.CACHE_NAMES)
            if not logical or not protected_path(logical,{'kind':'metadata'}):continue
            reason='test_config_or_dependency_in_cache'
        violations.append({'path':name,'reason':reason,'change_type':'created' if a is None else 'deleted' if z is None else 'modified'})
    return violations
