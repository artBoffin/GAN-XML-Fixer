#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coded by: Allan Gelman 
Concept by: Alexander Reben
Supported by: Stochastic Labs
"""

#! /usr/bin/env python
import argparse
import tool

def run(args):
    generated_txt = args.txt_input 
    invalid_svg_dir = args.idir_output 
    valid_svg_dir = args.vdir_output
    tool.txt_to_valid_svg_dir(generated_txt, invalid_svg_dir, valid_svg_dir)

def main():
    parser=argparse.ArgumentParser(description="Validate, Correct, and Classify generated SVG files")
    parser.add_argument("-txt",help="Path of generated text file trained on Scalable Vector Graphics (.svg files)" ,dest="txt_input", type=str, required=True)
    parser.add_argument("-idir",help="Path of the output invalid SVG directory. Default = invalid_svg" ,dest="idir_output", type=str, default="invalid_svg")
    parser.add_argument("-vdir",help="Path of the output valid SVG directory. Default = valid_svg" ,dest="vdir_output", type=str, default="valid_svg")
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)

if __name__=="__main__":
    main()