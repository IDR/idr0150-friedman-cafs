# idr0150-friedman-cafs

## Demo import workflow

Connect to the pilot (ssh command see SubmissionWorkflow/import.md)

Open browser (best private window to avoid caching issues) and go to: http://localhost:1080/webclient/?show=screen-102 .
This will directly open OMERO.web for a submission (to avoid waiting for the start page to load).

Create a screen session: `screen -S 150_<your name>` (give it a name, suggestion: the IDR number you're working on and your name)
You can 'detach' from the session with CTRL+A+D and 'reattach' later again with `screen -r 150_<your name>`

Clone repository: `git clone https://github.com/IDR/idr0150-friedman-cafs.git`
Checkout the demo branch:
```
cd idr0150-friedman-cafs
git checkout demo
```

Usually you would move it to /uod/idr/metadata but as it already exists there, just move it to /tmp
for the demo purpose: `mv idr0150-friedman-cafs /tmp/`

Switch to the omero-server user: `sudo su omero-server`
And go to the cloned repository: `cd /tmp/idr0150-friedman-cafs/experimentA`

Activate the virtual environment in order to have the OMERO CLI available: `source /opt/omero/server/venv3/bin/activate`

Create the Project: `omero obj new Project name=idr0150-friedman-cafs/experimentA`

This will give you the ID ("Project:1234"), but also double check in the browser. It's generally useful to check
after each step in the browser.

Create the Datasets: `/uod/idr/metadata/idr-utils/scripts/create_datasets.sh <Project ID> idr0150-experimentA-filePaths.tsv`

Start the import: `/opt/omero/server/OMERO.server/bin/omero import --bulk idr0150-experimentA-bulk.yml --file /tmp/150.log --errs /tmp/150.err`

Check the log file if the number of imported images match your expectation. Check the err file for errors. You'll see that there is a file
in the filepaths.tsv which doesn't exist. You'd have to check if it was added by mistake, if it was a typo, etc. You'd then push a fix to the
github repository. But the demo purpose is just to make you aware to check for import errors, no fix needed.

Check the annotation.csv: `python /uod/idr/metadata/idr-utils/scripts/annotate/check_annotations.py -v --skip-ok Project:<Project ID> idr0150-experimentA-annotation.csv` Check the output and fix errors (as the omero-server user can't edit the file, you have to either temporary `exit` or detach from the screen session).
Usually you would do that locally, push the fixes the github repository and check it out on the pilot again.

Add the annotations as OMERO.table: `omero metadata populate --report --batch 1000 --file idr0150-experimentA-annotation.csv Project:<Project ID>`

Create the map annotations: `omero metadata populate --context bulkmap --batch 100 --cfg idr0150-experimentA-bulkmap-config.yml Project:<Project ID>`

Apply the rendering settings: 
```
cd ../rendering_settings
omero render set Dataset:<ID of the TNBC dataset> TNBC.yml` (do the same for METABRIC)
```

Create the ROIs:
```
cd ../scripts
python add_rois.py
```

### Clean up

If you want to go through the workflow again, you have to clean up first.

The easiest option is to just rename the Project: `omero obj update Project:<Project ID> name=idr0150_old`

The cleaner option is to delete the Project. But you have to first unlink and remove the annotations.

Unlink annotations: `omero metadata populate --context deletemap --report --wait 300 --batch 100 --localcfg '{"ns":["openmicroscopy.org/mapr/organism", "openmicroscopy.org/mapr/antibody", "openmicroscopy.org/mapr/gene", "openmicroscopy.org/mapr/cell_line", "openmicroscopy.org/mapr/phenotype", "openmicroscopy.org/mapr/sirna", "openmicroscopy.org/mapr/compound", "openmicroscopy.org/mapr/protein", "openmicroscopy.org/mapr/orf", "openmicroscopy.org/mapr/OMAP"], "typesToIgnore":["Annotation"]}' --cfg idr0150-experimentA-bulkmap-config.yml Project:<Project ID>`

Remove annotations: `omero metadata populate --context deletemap --report --wait 300 --batch 100 --cfg idr0150-experimentA-bulkmap-config.yml Project:<Project ID>`

Delete Project: `omero delete --force Project:<Project ID>`
