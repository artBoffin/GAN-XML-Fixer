#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coded by: Allan Gelman 
Concept by: Alexander Reben
Supported by: Stochastic Labs
"""

import xmlschema
import os

def txt_to_invalid_svg_dir(generated_txt, invalid_svg_dir):
    
    """ 
    Converts the generated_txt to a directory individual svg files 
    
    generated_txt: name of text file of a collection of generated svg files
    invalid_svg_dir: path or name of desired directory to hold svg files
    """
    
    generated_txt = open(generated_txt, 'r')
    line = generated_txt.readline()

    #creating invalid_svg_dir if doesn't exist already
    if not os.path.exists(invalid_svg_dir):
        os.mkdir(invalid_svg_dir)
        print("Directory " , invalid_svg_dir ,  " Created ")
    else:    
        print("Directory " , invalid_svg_dir ,  " already exists")
    
    file_content = ""
    carry_over = ""
    num_files = 0
    
    while line:
        svg_end_tag_found = False
        last_line_content = ""
        index_end_of_last_line = 0
        
        #svg files don't need \n to be read properly
        if line != "\n":
            char_index = 0
            
            while char_index < len(line): 
                if line[char_index: char_index+6] == "</svg>":
                    svg_end_tag_found = True
                    index_end_of_last_line = char_index+6
                    
                    #the last line of a svg file ends with the </svg> end tag
                    last_line_content = line[:index_end_of_last_line]  
                    carry_over = line[index_end_of_last_line:]
                    
                    #carryover that contains end tags is handled by helper function 
                    #returns the left over carry_over to be added to the next file and the updated num_files 
                    if "</svg>" in carry_over:
                        carry_over, num_files = carry_over_to_files(carry_over, invalid_svg_dir, num_files)
                        break
                    
                char_index = char_index + 1 
                
            #building up files contained in generated_txt
            #the end of svg files is marked by the </svg> end tag
            if not svg_end_tag_found:
                file_content = file_content + line
            else:
                file_content = file_content + last_line_content             
                f = open(str(num_files)+".svg","w+")
                f.write(file_content)
                f.close()
                #moving all the files into the invalid_svg_dir since none of them have been validated yet
                os.rename(str(num_files) + ".svg", invalid_svg_dir + "/" + str(num_files)+".svg") 
                file_content = "" 
                
                for char in carry_over:
                    if char != "\n":
                        file_content  = file_content + char
                        
                num_files = num_files + 1 
                
        line = generated_txt.readline()
        
    generated_txt.close()
                    
    return None

def carry_over_to_files(carry_over, invalid_svg_dir, num_files):
    
    """ 
    Converts the carry_over to individual svg files place in the invalid_svg_dir
    
    carry_over: string of the carry_over text
    invalid_svg_dir: path or name of desired directory to hold svg files
    num_files: number to keep track of how many files created
    """
    
    char_index = 0 
    while carry_over[char_index: char_index+6] != "</svg>":
        char_index = char_index + 1 

    index_end_of_file = char_index+6 
    #the entire file is the carryover until the </svg> end tag
    file_content = carry_over[:index_end_of_file] 
    carry_over = carry_over[index_end_of_file:]
             
    f = open(str(num_files) + ".svg","w+")
    f.write(file_content)
    f.close()
    
    #moving all the files into the invalid_svg_dir since none of them have been validated yet
    os.rename(str(num_files) + ".svg", invalid_svg_dir + "/" + str(num_files) + ".svg") 
    
    #recursivley converts the carry_over to files until there is just carry_over without any </svg> end tags
    if "</svg>" in carry_over:
        return carry_over_to_files(carry_over, invalid_svg_dir, num_files+1)
    else:
        return (carry_over, num_files+1)

def invalid_svg_dir_to_valid_svg_dir(invalid_svg_dir, valid_svg_dir):
    
    """
    Classifies the svg files into invalid and valid, and attempts to correct invalid files.
    
    invalid_svg_dir: directory of invalid svg files
    valid_svg_dir: directory of valid svg files
    """
    
    #creating valid_svg_dir if doesn't exist already
    if not os.path.exists(valid_svg_dir):
        os.mkdir(valid_svg_dir)
        print("Directory " , valid_svg_dir ,  " Created ")
    else:    
        print("Directory " , valid_svg_dir ,  " already exists")
      
    #iterating through the files in invalid_svg_dir     
    for filename in os.listdir(invalid_svg_dir):       
        schema = xmlschema.XMLSchema('./svg-schema.xsd')
        try:
            valid = schema.is_valid(invalid_svg_dir + "/" + filename)
        except:
            valid = False
        #moving the validated files into valid_svg_dir
        if valid:            
            os.rename(invalid_svg_dir + "/" + filename, valid_svg_dir + "/" + filename)
        else:
            correction_attempt(filename, 1, invalid_svg_dir + "/" + filename, invalid_svg_dir, valid_svg_dir)
            
    return None

def correction_attempt(filename, num_attempts, path, invalid_svg_dir, valid_svg_dir):
   
    """
    Recursivley attemps to correct the svg file.
    
    filename: file attempting to be correct
    num_attempts: the amount of times the files has been corrected
    path: path of file
    invalid_svg_dir: directory of invalid svg files
    valid_svg_dir: directory of valid svg files
    """

    schema = xmlschema.XMLSchema('./svg-schema.xsd')
    f = open(str(num_attempts) + "x_corrected_" + filename,"w+")
    if num_attempts == 1:
        file_content = remove_g_tags(path)
    elif num_attempts == 2:
        file_content = fix_quote(path)
    elif num_attempts == 3:
        file_content = remove_redefined_attributes(path)
    elif num_attempts == 4:
        file_content = add_missing_path_end_tag(path)
    f.write(file_content)
    f.close()
    try:
        valid = schema.is_valid("./" + str(num_attempts) + "x_corrected_" + filename)
    except:
        valid = False
    #moving the validated files to valid_svg_dir
    #marking the corrected files with "num_attemptsx_corrected_" to indicate they have been modified num_attempts times
    #marking the original files with "orig_" to imply that their is a modified version in the valid_svg_dir
    if valid:
        os.rename(invalid_svg_dir + "/" + filename, invalid_svg_dir + "/" + "orig_" + filename) 
        os.rename(str(num_attempts) + "x_corrected_" + filename, valid_svg_dir + "/" + str(num_attempts) + "x_corrected_" + filename)
        return None
    #deleting the files that failed to be validated after correction
    #recursivley attempting to correct file 
    else:
        if num_attempts < 4:
            correction_attempt(filename, num_attempts+1, str(num_attempts) + "x_corrected_" + filename, invalid_svg_dir, valid_svg_dir)
            os.remove(str(num_attempts) + "x_corrected_" + filename)
        else:
            os.remove(str(num_attempts) + "x_corrected_" + filename)
            return None

def remove_g_tags(path): 
    
    """
    Removing all g-tags from the file.
    
    path: path of file being corrected
    """
    
    file_content = ""
    file = open(path, 'r')
    line = file.readline()
    
    while line:
        char_index = 0
        #passing through all the file except for the g-tags
        line_content = ""
        while char_index < len(line): 
            if line[char_index: char_index + 3] == "<g>":
                char_index=char_index + 3
            if line[char_index: char_index + 4] == "</g>":
                char_index=char_index + 4
                
            line_content = line_content + line[char_index]
            char_index = char_index + 1
            
        file_content = file_content + line_content
        line = file.readline()
    
    return file_content

def fix_quote(path):
    
    """
    Removing any extra quotation marks and adds any missing quotation marks
    
    path: path of file being corrected
    """
    
    chars_after_quote = ["/"," ", ">", "\n", "?"]
    start_quote_found = False
    file_content = ""
    file = open(path, 'r')
    
    for line in file:
        #passing through all the file except for the extra quotes
        i = 0
        line_content = ""
        while i < len(line): 
            #skipping over quote that comes after '=' that isn't a start quote
            if line[i] == '"' and line[i-1] != '=' and start_quote_found and line[i+1] in chars_after_quote:
                start_quote_found = False
            elif line[i] == '"' and line[i-1] == '=' and not start_quote_found:
                start_quote_found = True           
            elif line[i] == '"' and line[i-1] == '=' and start_quote_found:
                i = i + 1
                
            #skipping over any other quote that isn't a start or end quote   
            if line[i] == '"' and line[i-1] != '=' and line[i+1] not in chars_after_quote:
                i = i + 1 
            else:    
                line_content = line_content + line[i]
                
            #adding a quote for the last attribute if it doesn't have a closing quote
            if line[i+1:i+2] == '>' and line[i] != '"' and start_quote_found:
                line_content = line_content + '"'
                start_quote_found = False
            
            i = i + 1
            
        #building up file_content
        file_content = file_content + line_content
    return file_content

def remove_redefined_attributes(path):
    
    """
    Removing any redefined 'viewBox' or 'd' attributes
    
    path: path of file being corrected
    """   
    
    file_content = ""
    file = open(path, 'r')
    file = file.read()
    d_attribute_found = False
    view_box_attribute_found = False
    end_tag_found = False
    i = 0
    
    while i < len(file): 
        #keeping track of end tags, beacuse redefinitions occur within elements
        if file[i] == ">":
            end_tag_found = True
            d_attribute_found = False
            view_box_attribute_found = False
        if file[i] == "<":
            end_tag_found = False
        
        #skipping over d attribute
        if file[i:i+3] == 'd="' and not d_attribute_found: 
            d_attribute_found = True
            file_content = file_content + file[i]
            i = i + 1 
        elif file[i:i+3] == 'd="' and d_attribute_found and not end_tag_found: 
            i = i + 3
            while file[i] != '"':
                i = i + 1 
            i = i + 1    
        else:       
            #skipping over viewBox attribute
            if file[i:i+9] == 'viewBox="' and not view_box_attribute_found: 
                view_box_attribute_found = True
                file_content = file_content + file[i]
                i = i + 1 
            elif file[i:i+9] == 'viewBox="' and view_box_attribute_found and not end_tag_found: 
                i = i + 9
                while file[i] != '"':
                    i = i + 1 
                i = i + 1  
            else:
                file_content = file_content + file[i]
                i = i + 1   
    
    return file_content
    
def add_missing_path_end_tag(path):
    
    """
    Adding any missing path end tags
    
    path: path of file being corrected
    """
    
    file_content = ""
    file = open(path, 'r')
    path_start_tag_found = False
    
    for line in file:
        i = 0
        line_content = ""
        while i < len(line): 
            if line[i:i+5] == "<path" and not path_start_tag_found:
                path_start_tag_found = True
            if line[i] == ">" and path_start_tag_found and line [i+1: i+8] == "</path>":
                path_start_tag_found = False
            #adding path end tag
            elif line[i] == ">" and path_start_tag_found and line [i+1: i+8] != "</path>":
                path_start_tag_found = False
                line_content = line_content + line[i]
                line_content = line_content + "</path>"
                i = i + 1  
                continue
            
            line_content = line_content + line[i]
            i = i + 1   
            
        file_content = file_content + line_content
        
    return file_content
      
def txt_to_valid_svg_dir(generated_txt, invalid_svg_dir, valid_svg_dir):
    
    """
    Contains all the actions of this tool. Converting the text file to classified folders of svg files.
    
    generated_txt: name of text file of a collection of generated svg files
    invalid_svg_dir: directory of invalid svg files
    valid_svg_dir: directory of valid svg files
    """
    
    txt_to_invalid_svg_dir(generated_txt, invalid_svg_dir)
    invalid_svg_dir_to_valid_svg_dir(invalid_svg_dir, valid_svg_dir)

if __name__ == '__main__':  
    pass
