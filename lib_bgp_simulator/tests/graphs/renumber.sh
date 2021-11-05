#!/bin/bash

# Script will produce a bash script to the command line that you
# can copy and paste to execute and will do replacements on the 
# specified file.
# Example Output:
#
# cat graph_011.py |
# sed 's/24875/1/g' | 
# sed 's/52320/2/g' | 
# sed 's/12389/3/g' | 
# sed 's/174/4/g' | 
# sed 's/213371/5/g' | 
# sed 's/208673/6/g' | 
# sed 's/31133/7/g' | 
# sed 's/1299/8/g' | 
# sed 's/2914/9/g' | 
# sed 's/24875/10/g' | 
# sed 's/53180/11/g' | 
# sed 's/268337/12/g' | 
#
# You should copy the above (with exception of the last pipe character
# and paste this into command line and hit enter. It will output the file 
# with the renumbering).


#############################
# Input Arguments
#############################

# File that will have its ASNs renamed
file=${1};
# NOTE: Another argument is literally a list in the for loop
# NOTE: So in total there are 2 arguments needed for this program


#############################
# Main
#############################

# Initialize the replacement_asn
# This variable will be incremented within the loop of ASNs
# that need to be replaced. So each ASN in the list is given 
# a new ASN assigned from this incrementing variable.
replacement_asn=1;

# print out first part of output script
echo "cat $file |"

# Iterate over the ASNs that need to be replaced
# NOTE : If possible the list/vector of the items that need to replaced 
# can be an input parameter or automatically determined.
for num in do 24875 52320 12389 174 213371 208673 31133 1299 2914 24875 53180 268337
   echo "sed 's/${num}/${replacement_asn}/g' | "
   replacement_asn=$(($replacement_asn+1))
done

