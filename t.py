#!/usr/bin/env python

from __future__ import print_function
import shutil
import os
import sys
import json
import argparse

TEMPLATE_DIR = 'templates'
DESCRIPTION_FILE = '.templates'
IGNORE_LIST = [DESCRIPTION_FILE, '.DS_Store', '.', '..'] 
SETTINGS = os.path.join(os.path.expanduser('~'), '.t.py.settings')

def exists(template):
    template = os.path.join(TEMPLATE_DIR, template)
    return os.path.exists(template)


def copy_template(template, dst, overwrite=False):
    if exists(template):
        src = os.path.join(TEMPLATE_DIR, template)
        if os.path.exists(dst) and not overwrite:
            sys.exit(dst + ' already exists')

        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)
    else:
        sys.exit('Template ' + template + ' does not exist')


def list_templates():
    if os.path.exists(TEMPLATE_DIR):
        l = os.listdir(TEMPLATE_DIR)
        for i in IGNORE_LIST:
            if i in l:
                l.remove(i)
        if len(l) > 0:
            d = load_descriptions()
            for t in sorted(l):
                if t in d:
                    print(t, '-', d[t])
                else:
                    print(t)
        else:
            print('There are no templates in ', TEMPLATE_DIR)
    else:
        print('Directory', TEMPLATE_DIR, ' does not exist')
    print('')


def remove(template):
    if exists(template):
        d = load_descriptions()
        if template in d:
            del d[template]
            open(os.path.join(TEMPLATE_DIR, DESCRIPTION_FILE), 'w').write( json.dumps(d, sort_keys=True, indent=4) + os.linesep )
        t = os.path.join(TEMPLATE_DIR, template)
        if os.path.isdir(t):
            shutil.rmtree(t)
        else:
            os.remove(t)


def load_descriptions():
    p = os.path.join(TEMPLATE_DIR, DESCRIPTION_FILE)
    d = {}
    if os.path.exists(p):
        d = json.loads( open(p).read() )
    return d


def update_description(template, description):
    d = load_descriptions()
    if exists(template):
        if len(description) == 0:
            sys.exit('Please provide a description')
        else: 
            d[template] = description
            open(os.path.join(TEMPLATE_DIR, DESCRIPTION_FILE), 'w').write( json.dumps(d, sort_keys=True, indent=4) + os.linesep )
    else:
        sys.exit('Template ' + template + ' does not exist')


def add_template(src, template, description, overwrite=False):
    if os.path.exists(src):
        destination = os.path.join(TEMPLATE_DIR, template)
        if os.path.exists(destination) and not overwrite:
            sys.exit(template + ' already exists')
        else:
            if os.path.isdir(src):
                shutil.copytree(src, destination)
            else:
                shutil.copyfile(src, destination)

            if len(description) > 0:
                update_description(template, description)
    else:
        sys.exit('File ' + src + ' does not exist')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='A script to manage and copy templates of scripts.')
    parser.add_argument('-a', '--add', help='add a template')
    parser.add_argument('-n', '--name', help='name of template')
    parser.add_argument('-u', '--update', help='update a templates description')
    parser.add_argument('-R', '--remove', help='template to remove')
    parser.add_argument('-l', '--list', help='list templates', action='store_true')
    parser.add_argument('-o', '--overwrite', help='allow overwriting', action='store_true')
    parser.add_argument('-T', '--template_dir', help='template directory')
    parser.add_argument('args', nargs='*')
    options = parser.parse_args()
    
    if not options.template_dir and os.path.exists(SETTINGS):
        d = json.loads( open(SETTINGS).read() )
        TEMPLATE_DIR = d.get('template_dir', TEMPLATE_DIR)
    elif options.template_dir:
        TEMPLATE_DIR = options.template_dir

    # create template directory if it doesnt exist
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if options.list:
        list_templates()
    elif options.add:
        template_name = options.add.split(os.sep)[-1]
        if options.name:
            template_name = options.name
        add_template( options.add, template_name, ' '.join(options.args),
                overwrite=options.overwrite )
    elif options.update:
        update_description( options.update, ' '.join(options.args) )
    elif options.remove:
        remove(options.remove)
    elif len(options.args) == 2:
        copy_template(options.args[0], options.args[1])
    elif len(options.args) == 1:
        copy_template(options.args[0], os.path.join(os.getcwd(), options.args[0]))
    else:
        parser.print_help()
    
    
    
