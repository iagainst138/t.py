#!/usr/bin/env python

from __future__ import print_function
import argparse
import json
import os
import shutil
import sys

description_file_name = '.templates'


class Templates:
    def __init__(self):
        # TODO rename "t_dir"
        t_dir = os.path.join(os.path.expanduser('~'), '.t.py')
        if not os.path.exists(t_dir):
            self.initial_setup(t_dir)
        config_file = os.path.join(t_dir, 'config')
        config = json.loads(open(config_file).read())
        self.template_dir = config.get('template_dir')

        self.description_file = os.path.join(
            self.template_dir, description_file_name)
        self.ignore_list = [description_file_name, '.DS_Store', '.', '..']

    def initial_setup(self, t_dir):
        template_dir = os.path.join(t_dir, 'templates')
        os.makedirs(t_dir)
        os.makedirs(template_dir)
        config_file = os.path.join(t_dir, 'config')
        config = {
            'template_dir': template_dir,
        }
        open(config_file, 'w').write(
            json.dumps(config, sort_keys=True, indent=4) + os.linesep)

    def copy_template(self, template, dst, overwrite=False):
        if self.exists(template):
            src = os.path.join(self.template_dir, template)
            if os.path.exists(dst) and not overwrite:
                sys.exit('"{}" already exists'.format(dst))

            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        else:
            sys.exit('Template "{}" does not exist'.format(template))

    def list_templates(self):
        if os.path.exists(self.template_dir):
            templates = set(
                os.listdir(self.template_dir)).difference(set(self.ignore_list))
            if len(templates) > 0:
                descriptions = self.load_descriptions()
                for t in sorted(templates):
                    print('{:10} - {}'.format(t, descriptions.get(t, '')))
            else:
                print('There are no templates in {}'.format(self.template_dir))
        else:
            sys.exit('Directory {} does not exist'.format(self.template_dir))
        print('')

    def delete(self, template):
        if self.exists(template):
            d = self.load_descriptions()
            if template in d:
                del d[template]
                open(self.description_file, 'w').write(
                    json.dumps(d, sort_keys=True, indent=4) + os.linesep)
            t = os.path.join(self.template_dir, template)
            if os.path.isdir(t):
                shutil.rmtree(t)
            else:
                os.remove(t)
            print('Deleted {} from {}'.format(template, self.template_dir))

    def load_descriptions(self):
        d = {}
        if os.path.exists(self.description_file):
            d = json.loads(open(self.description_file).read())
        return d

    def update_description(self, template, description):
        d = self.load_descriptions()
        if self.exists(template):
            if len(description) == 0:
                sys.exit('Please provide a description')
            else:
                d[template] = description
                open(self.description_file, 'w').write(
                    json.dumps(d, sort_keys=True, indent=4) + os.linesep)
        else:
            sys.exit('Template "{}" does not exist'.format(template))

    def add_template(self, src, template_name, description, overwrite=False):
        if os.path.exists(src):
            destination = os.path.join(self.template_dir, template_name)
            if os.path.exists(destination) and not overwrite:
                sys.exit('Error: template {} already exists'.format(template_name))
            else:
                if os.path.isdir(src):
                    shutil.copytree(src, destination)
                else:
                    shutil.copyfile(src, destination)

                if len(description) > 0:
                    self.update_description(template_name, description)
                print('Added {} to {}'.format(template_name, self.template_dir))
        else:
            sys.exit('File "{}" does not exist'.format(src))

    def exists(self, template):
        template = os.path.join(self.template_dir, template)
        return os.path.exists(template)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='A script to manage and copy templates of scripts.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', help='add a template')
    parser.add_argument('-n', '--name', help='name of template')
    group.add_argument('-u', '--update', help='update a templates description')
    group.add_argument('-d', '--delete', help='template to delete')
    group.add_argument('-l', '--list', help='list templates',
        action='store_true')
    parser.add_argument('-o', '--overwrite', help='allow overwriting',
        action='store_true')
    parser.add_argument('args', nargs='*')
    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    t = Templates()

    if options.list:
        t.list_templates()
    elif options.add:
        template_name = options.add.split(os.sep)[-1]
        if options.name:
            template_name = options.name
        t.add_template(options.add, template_name, ' '.join(options.args),
                overwrite=options.overwrite)
    elif options.update:
        t.update_description(options.update, ' '.join(options.args))
    elif options.delete:
        t.delete(options.delete)
    elif len(options.args) == 2:
        t.copy_template(options.args[0], options.args[1], options.overwrite)
    else:
        parser.print_help()
