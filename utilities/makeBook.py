#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reconcile book6 chapters with contents, and set up inter-section
and inter-chapter links as far as possible."""

# Version: 2022-09-18 - original
# Version: 2022-09-26 - added {{{ }}} citations
# Version: 2022-10-05 - fencepost error when adding section to contents
# Version: 2022-10-06 - added citation expansion for chapter base file
# Version: 2022-11-09 - allow {{ }} as well as {{{ }}}
#                     - added citation of I-D. or draft-
# Version: 2022-11-15 - check that cited references exist (partial)
# Version: 2022-11-16 - improved reference checks (but still partial)
# Version: 2022-11-18 - small oversight in reference check
# Version: 2022-11-19 - cosmetic
# Version: 2022-11-20 - now checks I-D, BCP and STD refs
# Version: 2022-11-22 - fix oversights/nits in contents updating
# Version: 2022-11-27 - {{ }} now puts [ ] round citation
#                     - {{{ }}} does not put [ ]
#                     - fix missing newline when adding new section

########################################################
# Copyright (C) 2022 Brian E. Carpenter.                  
# All rights reserved.
#
# Redistribution and use in source and binary forms, with
# or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above
# copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials
# provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of
# its contributors may be used to endorse or promote products
# derived from this software without specific prior written
# permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS  
# AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED 
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A     
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)    
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING   
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE        
# POSSIBILITY OF SUCH DAMAGE.                         
#                                                     
########################################################

from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askokcancel, askyesno, showinfo

import time
import os
import urllib.request

def logit(msg):
    """Add a message to the log file"""
    global flog, printing
    flog.write(msg+"\n")
    if printing:
        print(msg)
        
def logitw(msg):
    """Add a warning message to the log file"""
    global warnings
    logit("WARNING: "+msg)
    warnings += 1

def dprint(*msg):
    """ Diagnostic print """
    global printing
    if printing:
        print(*msg)

def crash(msg):
    """Log and crash"""
    printing = True
    logit("CRASH "+msg)
    flog.close()
    exit()    

def rf(f):
    """Return a file as a list of strings"""
    file = open(f, "r",encoding='utf-8', errors='replace')
    l = file.readlines()
    file.close()
    #ensure last line has a newline
    if l[-1][-1] != "\n":
        l[-1] += "\n"
    return l


def wf(f,l):
    """Write list of strings to file"""
    global written
    file = open(f, "w",encoding='utf-8')
    for line in l:
        file.write(line)
    file.close()
    logit("'"+f+"' written")
    written +=1 

def uncase(l):
    """Return lower case version of a list of strings"""
    u = []
    for s in l:
        u.append(s.lower())
    return u

def make_basenames():
    """Make or refresh base names"""
    global base_names, base
    base_names = []
    for bline in base:
        if len(bline) < 4:
            continue
        bline = bline.strip("\n")
        if bline.startswith("## ["):
            # existing section reference
            sname,_ = bline.split("[", maxsplit = 1)[1].split("]", maxsplit = 1)
            base_names.append(sname)
        elif bline.startswith("##") and not "###" in bline:
            #possible section
            try:
                _,sname = bline.split(" ", maxsplit=1)
            except:
                continue
            #treat as new section (will create file later)
            base_names.append(sname)
    dprint("Base names: ", base_names)

def link_text(prev, nxt, chapter):
    """Construct link for end of a section"""
    part1 = ""
    part2 = ""
    if prev:
        part1 = " [<ins>Previous</ins>]("+prev.replace(" ","%20")+".md)"
    if nxt:
        part2 = " [<ins>Next</ins>]("+nxt.replace(" ","%20")+".md)"     
    return "###"+part1+part2+" [<ins>Chapter Contents</ins>]("+chapter.replace(" ","%20")+".md)"

link_warn = "<!-- Link lines generated automatically; do not delete -->\n"

def url_ok(url):
    """Check if a URL is OK"""
    try:
        response = urllib.request.urlopen(url).getcode()
    except:
        return False  #URL doesn't exist
    return response==200

def rfc_ok(s):
    """Check if an RFC etc. is real"""
    global rfcs_checkable
    if not rfcs_checkable:
        return True  #because we can't check on line right now
    dprint("Checking", s)
    if s[:3] == "BCP" or s[:3] == "STD":
        url = 'https://www.rfc-editor.org/refs/ref-'+s.lower()+'.txt'
    elif s[:3] == "RFC":

##    #clumsy method dropped...
##    if len(s) < 7:
##        #needs leading zeroes for DOI check
##        s = "RFC" + s[3:].zfill(4)    
##    url = "https://doi.org/10.17487/" + s
##    try:
##        response = urllib.request.urlopen(url).getcode()
##    except:
##        return False  #DOI not assigned, hence no RFC
##    return response==200

        s = s.replace('RFC','RFC.')
        url = 'https://www.rfc-editor.org/refs/bibxml/reference.'+s+'.xml'
    else:
        return(False)  #invalid call
    return url_ok(url)

def draft_ok(s):
    """Check if a draft is real"""
    global drafts_checkable
    if not drafts_checkable:
        return True  #because we can't check on line right now
    dprint("Checking", s)
    #remove revision number if present
    if s[-3] == '-' and s[-2].isdigit() and s[-1].isdigit():
        s = s[:-3]
    url = 'https://bib.ietf.org/public/rfc/bibxml3/reference.I-D.'+s+'.xml'
    return url_ok(url)



def file_ok(fn):
    """Check if a local file is OK"""
    if fn.startswith("../"):
        fn = fn.replace("../","")
    fn = fn.replace("%20"," ")
    return os.path.exists(fn)
    

def expand_cites():
    """Look for kramdown-style citations and expand them"""
    global section, contents, file_names, topic_file
    schange = False
    for i in range(len(section)):
        lchange = False
        line = section[i]
        if "  {{" in line:
            continue        #ignore a line that looks like documentation of {{ or {{{ itself        
        try:
            #convert {{ }} to \[{{ }}]
            line = line.replace("{{{","{?x{").replace("}}}","}?y}")
            line = line.replace("{{","\[{{").replace("}}","}}]")
            line = line.replace("{?x{","{{").replace("}?y}","}}")
            if line.count("{{") != line.count("}}"):
                logitw("Malformed reference in "+topic_file)
            while "{{" in line and "}}" in line:
                #dprint("Citation  in:", line)
                #found an expandable citation
                head, body = line.split("{{", maxsplit=1)
                cite, tail = body.split("}}", maxsplit=1)
                if cite.startswith("RFC") or cite.startswith("BCP") or cite.startswith("STD"):
                    if not rfc_ok(cite):
                        logitw(cite+" not found on line")
                    cite = "["+cite+"](https://www.rfc-editor.org/info/"+cite.lower()+")"
                    line = head + cite + tail
                    lchange = True
                elif cite.startswith("I-D."):
                    draft_name = cite[4:]
                    cite = "["+cite+"](https://datatracker.ietf.org/doc/draft-"+draft_name+"/)"
                    if not draft_ok(draft_name):
                        logitw(draft_name+" not found on line")
                    line = head + cite + tail
                    lchange = True
                elif cite.startswith("draft-"):
                    draft_name = cite[6:]
                    if not draft_ok(draft_name):
                        logitw(cite+" not found on line")
                    cite = "["+cite+"](https://datatracker.ietf.org/doc/"+cite+"/)"
                    line = head + cite + tail
                    lchange = True

                elif cite[0].isdigit():
                    #print("Found chapter?", cite)
                    found_c = False
                    #extract chapter number
                    if ". " in cite:
                        cnum, sname = cite.split(". ", maxsplit=1)      
                        #derive chapter name
                        for cline in contents:
                            if "["+cnum+"." in cline:
                                chap = cline.split("(")[1].split("/")[0]
                                fn = "../"+chap+"/"+sname.replace(" ","%20")+".md"
                                if not file_ok(fn):
                                    logitw('"'+cite+'" not found')
                                cite = "["+cite+"]("+fn+")"
                                line = head + cite + tail
                                lchange = True
                                found_c = True
                                break
                    if not found_c:
                        #Bogus chapter number
                        line = head + "[" + cite + "](TBD)" + tail
                        lchange = True
                        logitw('"'+cite+'" reference could not be resolved')
                            
                else:
                    #maybe it's a section name
                    #print("Found section?", cite)
                    if cite in file_names:
                        cite = "["+cite+"]("+cite.replace(" ","%20")+".md)"
                        line = head + cite + tail
                        lchange = True
                    else:
                        #print("Found nothing")
                        line = head + "[" + cite + "](TBD)" + tail
                        lchange = True
                        logitw('"'+cite+'" reference could not be resolved')
        except:
            #malformed line, do nothing
            pass
        if lchange:
            section[i] = line
            schange = True
            
    return schange

######### Startup

#Define some globals

printing = False # True for extra diagnostic prints
base = []        # the base file for each chapter
base_names = []  # the section names extracted from the base file
warnings = 0     # counts warnings in the log file
written = 0      # counts files written

#Announce

Tk().withdraw() # we don't want a full GUI

T = "Book reconciler and link maker."

printing = askyesno(title=T,
                    message = "Diagnostic printing?")

where = askdirectory(title = "Select main book directory")
                   
os.chdir(where)

#Open log file

flog = open("makeBook.log", "w",encoding='utf-8')
logit("makeBook run at "
      +time.strftime("%Y-%m-%d %H:%M:%S UTC%z",time.localtime()))

logit("Running in directory "+ os.getcwd())


showinfo(title=T,
         message = "Will read in current contents.\nChecking new references can be slow.\nTouch no files until done!")

#Can we check RFCs?

rfcs_checkable = True
rfcs_checkable = rfc_ok("RFC8200")
if not rfcs_checkable:
    logitw("Cannot check RFC existence on-line")

drafts_checkable = url_ok("https://bib.ietf.org")
if not drafts_checkable:
    logitw("Cannot check drafts' existence on-line")

######### Read previous contents

contents = rf("Contents.md")

######### Scan contents and decorate any plain chapter headings

contents_changed = False

#Get rid of blank lines in the working copy
contents[:] = (l for l in contents if l != "\n")

for i in range(len(contents)):
    l = contents[i]
    if l[0].isdigit():
        # Found a plain chapter title - change to link format
        l = l[:-1] #remove newline
        try:
            _, _ = l.split(" ", maxsplit = 1)
        except:
            if not askokcancel(title=T,        
                   message = "Suspect chapter title: "+l+"\nOK to continue?"):
                crash(l+": bad chapter title, abandoned make")
        l = "["+l+"]("+l.replace(" ","%20")+")\n"
        contents[i] = l
        contents_changed = True

        
######### Scan contents and create any missing directories,
######### build chapter list, extract sections lists

chapters = []

contentx = -1                      # Note that contents may expand or contract
while contentx < len(contents)-1:  # dynamically, so we control the loop count
    contentx += 1                  # explicitly as we go.
    cline = contents[contentx]
    if cline[0] == "[" and cline[1].isdigit():
        # Found a decorated chapter title - extract directory name
        dname = cline.split("(")[1].split("/")[0].replace("%20"," ")
        chapters.append(dname)
        #Need to create directory?
        if not os.path.isdir(dname):
            os.mkdir(dname)        #create empty directory
            logit("Created directory "+dname)
            #create base file
            base = []
            base.append("# "+dname+"\n\n")
            base.append("General introduction to this chapter.\n\n")
            base.append("<!-- ## Name (add plain section names like that) -->\n\n")
            base.append(link_warn)
            base.append("### [<ins>Back to main Contents</ins>](../Contents.md)\n")
            wf(dname+"/"+dname+".md", base)
        else:
            # read the base file
            base = rf(dname+"/"+dname+".md")
            logit("Processing '"+dname+"'")
            
        base_changed = False

        #Does the base end with the contents link?
        if not "### [<ins>Back to main" in base[-1]:
            base.append(link_warn)
            base.append("### [<ins>Back to main Contents</ins>](../Contents.md)\n")
            base_changed = True
        
        #extract section names from base file
        make_basenames()
                        
        #extract section names for existing files
        file_names = []
        
        for fname in os.listdir(dname):
            if os.path.isfile(os.path.join(dname, fname)):
                if ".md" in fname and fname[-3:] == ".md" \
                        and fname[:-3].lower() != dname.lower():                    
                    file_names.append(fname[:-3])
        dprint("Files", file_names)
                
        #extract section names from Contents.md
        contents_names = []
        first_namex = None
        savex = contentx  #in case no contents provided
        #N.B. loop within loop on contents list
        while contentx < len(contents)-1:
            contentx +=1
            cline = contents[contentx]
            if " " in cline and cline[0] == "*":
                #found a section name
                contents_names.append(cline.split(" ", maxsplit=1)[1][:-1])
                if not first_namex:
                    first_namex = contentx
                last_namex = contentx               
            else:
                #not a section
                if cline[0].isdigit() or cline[0] == "[":
                    #next chapter, restore outer loop index
                    contentx -= 1                    
                else:
                    if cline.strip(" ").strip("\n"):
                        logitw("Unexpected contents entry under '"+dname+"': '"+cline[:-1]+"'")
                break
                
        dprint("Contents", contents_names)

        if not len(contents_names):
            #Contents empty so far, set pointer for any new contents
            first_namex = savex
                    
        #Make uncased versions for comparisons    
        u_base_names = uncase(base_names)
        u_contents_names = uncase(contents_names)        

        if u_base_names != u_contents_names:
            #Reconciliation needed. Both names and order
            #should be the same. Priority to the base names.
            logit("Reconciling base and contents for '"+dname+"'")
          
            if set(u_base_names) == set(u_contents_names):
                #The discrepancy is that the contents names are out of order
                logitw("Contents for '"+dname+"' re-ordered")
                contents_names = base_names
                #now update section list in contents file
                contents_slice = []
                for i in range(len(contents_names)):
                    contents_slice.append('* ' + contents_names[i] + "\n")
                contents[first_namex:last_namex+1] = contents_slice
                contents_changed = True
            else:
                if len(base_names) >= len(contents_names):
                    #section(s) missing from contents?
                    for ib in range(len(base_names)):
                        if not u_base_names[ib] in u_contents_names:
                            #found missing section - add to contents
                            if contents_names == []:
                                ibx = savex+1
                            else:
                                ibx = first_namex+ib
                            contents_names[ib:ib] = [base_names[ib]]
                            u_contents_names = uncase(contents_names) 
                            contents[ibx:ibx] = ['* '+base_names[ib]+'\n']
                            contentx += 1  #advance outer loop counter
                            contents_changed = True
                            logit("Added '"+base_names[ib]+"' to '"+dname+"' contents")
                    #base_names and content_names now of equal length
                    dprint("Contents names again", contents_names)
                    
                            
                if len(base_names) <= len(contents_names):
                    #section(s) missing from base?
                    before = ""
                    for ic in range(len(contents_names)):
                        if not u_contents_names[ic] in u_base_names:
                            #found missing section - add to base file
                            mdfile = contents_names[ic].replace(" ","%20")+".md"
                            news = "\n## ["+contents_names[ic]+"]("+mdfile+")"
                            dprint("New", news, before)
                            #find correct place in base and insert
                            for ib in range(len(base)):
                                u_base = uncase(base)
                                if "<!--" in base[ib]:
                                    continue
                                if "### [<ins>Back" in base[ib]:
                                    #we're at the end already - stick it in
                                    base[ib:ib] = [news+"\n"]
                                    break                                    
                                if not "##" in base[ib]:
                                    if ib == len(base)-1:
                                        #last line, nothing found
                                        base[ib+1:ib+1] = [news+"\n"]
                                        break
                                    else:
                                        continue
                                if "## ["+before+"]" in u_base[ib]:
                                    base[ib+1:ib+1] = [news+"\n"]
                                    break
                            logit("Added '"+contents_names[ic]+"' to '"+dname+"' base file")
                            #dprint(base)
                            base_changed = True
                        before = contents_names[ic].lower()

        #Maybe update base_names
        if base_changed:
            make_basenames()                           

        #Make uncased versions for comparisons    
        u_base_names = uncase(base_names)
        u_file_names = uncase(file_names)

        if set(base_names) != set(file_names):
            #reconciliation needed
            logit("Reconciling base and files for '"+dname+"'")

            #Create a dictionary in case of file-name case discrepancies
            fndict = {}

            #Look for discrepant or missing filenames
            for topic in file_names:
                if (not topic in base_names) and topic.lower() in u_base_names:
                    #we have a file-name case discrepancy
                    logitw("File-name case discrepancy for '"+dname+"/"+topic+"'")
                    fndict[topic.lower()] = topic
                elif not topic in base_names:
                    #found a new topic
                    logit("New section '"+topic+"' added to base '"+dname+"'")
                    new_sec = "\n## ["+topic+"]("+topic.replace(" ","%20")+".md)\n"
                    for bx in range(len(base)):
                        if "### [<ins>Back" in base[bx]:
                            base[bx-1:bx-1] = [new_sec]
                            base_changed = True
                            break
                    
                    logitw("Run makeBook again to update main contents with new section")

            #Maybe update base_names
            if base_changed:
                make_basenames()
                u_base_names = uncase(base_names)

            #Look for runt sections in base and create files
            for topic in base_names:
                if not topic.lower() in u_file_names:
                    #There is no file, make it
                    new_md = []
                    new_md.append('## '+topic+"\n\n")
                    new_md.append("Section text goes here\n\n")
                    new_md.append(link_warn)
                    new_md.append(link_text("PREVIOUS","NEXT",dname))
                    wf(dname+"/"+topic+".md", new_md)
                    #Add link to file in base
                    for bx in range(len(base)):
                        if "## "+topic in base[bx]:
                            base[bx] = "## ["+topic+"]("+topic.replace(" ","%20")+".md)\n"
                            base_changed = True
                            break
                    #Add file name
                    file_names.append(topic)
                    u_file_names = uncase(file_names)
              
        if base_changed:
            wf(dname+"/"+dname+".md", base)

        #Now fixup link lines in section files. The only safe way
        #is to read them all and write back if fixed.

        #Assertion: base names and file names now match except for any case discrepancies

        if set(u_base_names) != set(u_file_names):
            dprint(dname, "Base names", base_names)
            dprint(dname, "File names", file_names)
            crash("Fatal base and file names mismatch in '"+dname+"'")

        #The sections are by definition in the order shown in the chapter base

        #Make a list of file names sorted like the base names
        #(Necessary because of possible case discrepancies)
        sorted_file_names = []
        for topic in base_names:
            try:
                #get actual file name from dictionary
                sorted_file_names.append(fndict[topic.lower()])
            except:
                #not in dictionary, so no case discrepancy
                sorted_file_names.append(topic)
        

        #Make the link line for each section
        #and update section file if necessary.
        #Also expand "kramdown" citations.
        for bx in range(len(base_names)):
            topic = base_names[bx]
            topic_file = sorted_file_names[bx]
            #is there a previous  topic?
            if bx == 0:
                previous = None
            else:
                previous = sorted_file_names[bx-1]
            #is there a subsequent topic?
            if bx == len(base_names)-1:
                nxt = None
            else:
                nxt = sorted_file_names[bx+1] 
            link_line = link_text(previous, nxt, dname)

            section = rf(dname+"/"+topic_file+".md")
            section_changed = expand_cites()
            if "### [<ins>" in section[-1]:
                #replace existing link line if necessary
                if section[-1].strip("\n") != link_line:
                    section[-1] = link_line
                    section_changed = True
            else:
                #add new link line
                section.append(link_warn)
                section.append(link_line)
                section_changed = True
                
            if section_changed:
                wf(dname+"/"+topic_file+".md", section)

        #Expand citations for chapter base file itself
        section = rf(dname+"/"+dname+".md")
        topic_file = dname #used by expand_cites()
        if expand_cites():
            wf(dname+"/"+dname+".md", section)
                    
######### Rewrite contents if necessary

if contents_changed:
    #ensure there is a blank line before each link or # title
    for i in range(1,len(contents)):
        if contents[i].startswith("[") or contents[i].startswith("#"):
            contents[i] = "\n"+contents[i]
    #and write it back                   
    wf("Contents.md", contents)
    contents_changed = False             
             
######### Close log and exit
    
flog.close()

if warnings:
    warn = str(warnings)+" warning(s)\n"
else:
    warn = ""

if written:
    wrote = str(written)+" file(s) written.\n"
else:
    wrote = "Clean run.\n"

showinfo(title=T,
         message = wrote+warn+"Check makeBook.log.")

