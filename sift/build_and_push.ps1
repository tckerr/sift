rm -r siftpy.egg-info
rm -r dist
python $PSScriptRoot/setup.py sdist
twine upload $PSScriptRoot/dist/*