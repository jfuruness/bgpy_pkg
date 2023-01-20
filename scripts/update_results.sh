#!/bin/bash

overleaf_dir="./6352b3da198d914e49175712"  # TODO: Replace with your path repo
output_dir="${overleaf_dir}/testing"  # This is where the extracted figures will be put
graphs_zip_files_path="this_is_a_place_holder_string_set_with_args_loop_below"
usage_information="script usage: $(basename \${0}) [-n graph-zip-files-path] [-u graph-zip-file]"

# Based on the flag entered do the following for the updates
while getopts 'u:h' OPTION; do
  case "$OPTION" in
    u)  # Update plots
      echo "Updating plots"
      graphs_zip_files_path=$OPTARG
      ;;
	h)  # Help (Usage information)
	  echo $usage_information
	  ;;
    ?)
      echo $usage_information >&2
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

# Stole from stackoverflow
# https://stackoverflow.com/questions/11279423/bash-getopts-with-multiple-and-mandatory-options
if ((OPTIND == 1))
then
    echo "No options specified"
    exit 1
fi
shift $((OPTIND - 1))

# Pull Latest Changes
cd $overleaf_dir
echo "Pulling latest changes from Overleaf"
git pull origin master

# Confirm changes are pulled
read -p "Ctrl-C to cancel or Enter to Proceed"

# Unzip results
for zip_file in $(ls $graphs_zip_files_path)
do
    unzip $graphs_zip_files_path/$zip_file
    # Copy over all results files
    dst=$output_dir/$(echo ${zip_file} | cut -f 1 -d '.')
    mv *.png $dst
    # Graphs copied over
    echo "Graphs from ${zip_file} copied over to overleaf ${dst}"
done


# Check for differences
git status

# Check the status and confirm changes
git status
read -p "Ctrl-C to cancel git changes"

# Commit and Push changes
echo "Commiting changes"
git add .
git commit -m "plots updates"
echo "Pushing changes to Overleaf"
git push origin master

