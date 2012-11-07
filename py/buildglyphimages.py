#!/usr/bin/env python

# ########################################################################
#                                                                        #
#      This file is part of the 'lilyglyphs' LaTeX package.              #
#                                ==========                              #
#                                                                        #
#              https://github.com/uliska/lilyglyphs                      #
#                                                                        #
#  Copyright 2012 by Urs Liska, git@ursliska.de                          #
#                                                                        #
#  'lilyglyphs' is free software: you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation, either version 3 of the License, or     #
#  (at your option) any later version.                                   #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
#  GNU General Public License for more details.                          #
#                                                                        #
#  You should have received a copy of the GNU General Public License     #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                        #
# ########################################################################

import os, sys,  getopt,  datetime,  subprocess

# ################
# Global variables

# base dir of the lilyglyphs package
lilyglyphs_root = ''

# flags
flag_force = False

# files with the glyph definitions
input_files = []
definitions_file = []

# LilyPond commands
lily_cmds = {}
# LaTeX commands
latex_cmds = {}

# ###############
# Used constants

# Directories
out_lysrc = 'generated_src'
out_images = 'pdfs'

# Strings

lilyglyphs_copyright_string = """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                                        %
%      This file is part of the 'lilyglyphs' LaTeX package.              %
%                                ==========                              %
%                                                                        %
%              https://github.com/uliska/lilyglyphs                      %
%                                                                        %
%  Copyright 2012 by Urs Liska, git@ursliska.de                          %
%                                                                        %
%  'lilyglyphs' is free software: you can redistribute it and/or modify  %
%  it under the terms of the GNU General Public License as published by  %
%  the Free Software Foundation, either version 3 of the License, or     %
%  (at your option) any later version.                                   %
%                                                                        %
%  This program is distributed in the hope that it will be useful,       %
%  but WITHOUT ANY WARRANTY; without even the implied warranty of        %
%  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          %
%  GNU General Public License for more details.                          %
%                                                                        %
%  You should have received a copy of the GNU General Public License     %
%  along with this program.  If not, see <http://www.gnu.org/licenses/>. %
%                                                                        %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

# string to be printed before the actual command
lily_src_prefix = """\\version "2.17.4"

#(set-global-staff-size 14)

\paper {
  indent = 0
}
\header {
  tagline = ""
}

"""

# string to be printed after the actual command definition
lily_src_score = """
  \\score {
  \\new Staff \\with {
    \\remove "Staff_symbol_engraver"
    \\remove "Clef_engraver"
    \\remove "Time_signature_engraver"
  }
"""

def main(argv):
    global flag_force, definitions_file_name
    short_options = 'i:'
    long_options = []
    long_options.append('input=')
    try:
        opts, args = getopt.getopt(argv, short_options, long_options)
        for opt, arg in opts:
            if opt in ("-i",  "--input"):
                input_files.append(arg)
            else:
                usage()
                sys.exit(2)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Do the actual work of the script
    print ''
    print 'buildglyphimages.py,'
    print 'Part of lilyglyphs.'

    print ''
    print 'Checking paths'
    check_paths()

    for input_file_name in input_files:
        print ''
        print 'Read input file ' + input_file_name
        read_input_file('definitions/' + input_file_name)

    print ''
    print 'Read entries of LilyPond commands:'
    read_entries()

    print ''
    print 'Write .ly files for each entry:'
    write_lily_src_files()

    print ''
    print 'Compile .ly files for each entry:'
    compile_lily_files()

    print ''
    print 'Clean up unused files'
    cleanup_lily_files()

    print ''
    print 'Create LaTeX commands'
    generate_latex_templates()

    print ''
    print 'Write LaTeX file'
    write_latex_file()


def check_paths():
    global lilyglyphs_root

    # check current working dir
    cwd = os.getcwd()
    if not 'lilyglyphs' in cwd:
        print 'Your current working directory seems to be wrong.'
        print 'Please cd to a location in the lilyglyphs directory.'
        sys.exit(2)

    lilyglyphs_root = cwd[:cwd.find('lilyglyphs') + 11]
    os.chdir(lilyglyphs_root + 'glyphimages')




    # check the presence of the necessary subdirectories
    # and create them if necessary
    # (otherwise we'll get errors when trying to write in them)
    ls = os.listdir('.')
    if not 'generated_src' in ls:
        os.mkdir('generated_src')
    if not 'pdfs' in ls:
        os.mkdir('pdfs')
    if not 'stash' in ls:
        os.mkdir('stash')



def cleanup_lily_files():
    """Removes unneccessary files from LilyPond compilation,
    rename and remove the preview PDF files to the right directory."""
    dir_in = out_lysrc + '/'
    dir_out = out_images + '/'
    file_list = os.listdir(dir_in)

    print 'Remove intermediate files'
    for file in file_list:
        dummy, extension = os.path.splitext(file)
        if not extension in ['.pdf', '.ly']:
            os.remove(dir_in + file)

    print 'Clean up:'
    for command_name in lily_cmds:
        print '- ' + command_name
        # remove full-page pdf
        os.remove(dir_in + command_name + '.pdf')
        # rename/move small 'preview' pdf
        os.rename(dir_in + command_name + '.preview.pdf',  dir_out + command_name + '.pdf')


def compile_lily_files():
    """Compiles all newly written .ly files"""
    for command_name in lily_cmds:
        args = []
        args.append("lilypond")
        args.append("-o")
        args.append("generated_src")
        args.append("-dpreview")
        args.append("-dno-point-and-click")
        args.append("generated_src/" + command_name + ".ly")
        subprocess.call(args)
        print ''

def generate_latex_templates():
    """Writes templates for the commands in a new LaTeX file.
    These should manually be moved to the appropriate .inp files
    in lilyglyphs"""

    # template string to build the command from
    # 'CMD' will be replaced by the actual command_name
    cmd_template = """\\newcommand*{\\CMDBase}[1][]{%
    \\setkeys{lilyDesignOptions}{scale=0.9,raise=-0.2}%
    \\lilyPrintImage[#1]{CMD}%
}
\\newcommand*{\\CMD}[1][]{\\CMDBase[#1] }
\\WithSuffix\\newcommand\\CMD*[1][]{\\CMDBase[#1]}

"""

    # template string to build the test code for the commands
    # 'CMD' will be replaced by the actual command_name
    testcode_template = """

\\noindent\\textbf{\\textsf{Continuous text for} \\cmd{CMD}:}\\\\
Lorem ipsum dolor sit amet, consectetur adipisicing elit,
sed \\CMD do eiusmod tempor incididunt ut labore et dolore magna aliqua \\CMD*.\\\\
\\CMD Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur\\CMD.
\\CMD Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

\\bigskip
"""

    for command_name in lily_cmds:
        latex_cmds[command_name] = []

        # create LaTeX command
        cmd = []
        cmd.append('% ' + str(lily_cmds[command_name][0])[2:-2] + '\n')
        cmd.append(signature() + '\n')
        cmd.append(cmd_template.replace('CMD', command_name))
        latex_cmds[command_name].append(cmd)

        # create documentation table

        # create LaTeX test code
        tc = []
        tc.append(testcode_template.replace('CMD', command_name))
        latex_cmds[command_name].append(tc)


def read_entries():
    """Parses the input source file and extracts glyph entries"""
    for i in range(len(definitions_file)):
        if '% lilyglyphs entry' in definitions_file[i]:
            i = read_entry(i)


def read_entry(i):
    """Reads a single glyph entry from the input file and stores it
    in the global dictionary lily_cmds"""
    global lily_cmds
    # read comment line(s)
    comment = []
    while True:
        i += 1
        cur_line = definitions_file[i].strip()
        # check for 'protected' entries that shouldn't be processed newly
        if '%%protected' in cur_line:
            is_protected = True
            i += 1
            cur_line = definitions_file[i].strip()
        else:
            is_protected = False
        first_line = cur_line.find('%{')
        if first_line >= 0:
            cur_line = cur_line[first_line + 3 :]
        last_line = cur_line.find('%}')
        if last_line >= 0:
            comment.append(cur_line[: last_line].strip())
            break
        else:
            comment.append(cur_line)
    i += 1
    # read command name
    cur_line = definitions_file[i].strip()
    command_name = cur_line[: cur_line.find('=') - 1]
    if is_protected:
        print '| protected and skipped: ' + command_name
        return i
    print '- ' + command_name
    # read actual command until we find a line the begins with a closing curly bracket
    i += 1
    lilySrc = []
    while definitions_file[i][0] != '}':
        lilySrc.append(definitions_file[i])
        i += 1
    lily_cmds[command_name] = [comment,  lilySrc]
    return i


def read_input_file(in_file):
    """Reads the input source file and stores it"""

    # check for existence of input file
    if not os.path.exists(in_file):
                    print 'File ' + in_file + ' not found.'
                    print 'Please specify an input file'
                    usage()
                    sys.exit(2)

    global definitions_file
    fin = open(in_file,  'r')
    for line in fin:
        definitions_file.append(line.rstrip(' \n'))
    fin.close()

def signature():
    """Returns a signature to be inserted in an output file"""
    return '% created by buildglyphimages.py on ' + str(datetime.date.today())

def usage():
    print """buildglyphimages. Part of the lilyglyphs package.
    Parses a .lysrc (lilyglyphs source) file, creates
    single .ly files from it, uses LilyPond to create single glyph
    pdf files and set up template files to be used in LaTeX.
    For detailed instructions refer to the manual.
    Usage:
    -i filename --input=filename (mandatory): Specifies the input file.
    -f --force: overwrite files if they already exist
    """

def write_file_info(name, fout):
    """Formats file specific information for the lilyPond source file"""
    long_line = '% This file defines a single glyph to be created with LilyPond: %\n'
    width = len(long_line) - 1
    header = '%' * width + '\n'
    spacer = '%' + ' ' * (width - 2) + '%\n'
    padding = width - len(name) - 8
    fout.write(header)
    fout.write(spacer)
    fout.write(long_line)
    fout.write(spacer)
    fout.write('%   ' + name + '.ly' + ' ' * padding + '%\n')
    fout.write(spacer)
    fout.write(header)
    fout.write(signature())
    fout.write('\n\n')

def write_latex_file():
    fout = open('stash/01_newImageGlyphs.tex', 'w')
    fout.write('% New Image Glyphs for the lilyglyphs package\n')
    fout.write(signature() + '\n')
    fout.write("""
% This file contains definitions for the new commands
% along with test code for them.
% You can test the commands in the context of continuous text
% and adjust their design time options.
% Afterwards you should manually move the commands to
% the appropriate .inp files,
% because this file will be overwritten by the next run
% of buildglyphimages.py!
% If you want to keep this file for reference
% you should save it with a new name.
%
% There also is a table containing entries for use in the lilyglyph manual.
% You can either copy the whole table to the appropriate
% place in lilyglyphs.tex or just copy individual table rows.

\\documentclass{scrartcl}
\\usepackage{lilyglyphsStyle}

%%%%%%%%%%%%%%%%%%%%%%%%%
% new command definitions

""")
    rand_cmds = []
    for command_name in latex_cmds:
        for line in latex_cmds[command_name][0]:
            fout.write(line)

    fout.write("""

\\begin{document}

%%%%%%%%%%%%%
% Text output

\\section*{New \\lilyglyphs{} commands}
""")
    fout.write(signature()[2:]+ '\n')
    fout.write("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Reference table to be used in the manual
% (use complete or single lines)

\\begin{reftable}{New commands}{newcommands}
""")
    row_template = '\\CMD & \\cmd{CMD} & description\\\\'
    for command_name in latex_cmds:
        fout.write(row_template.replace('CMD', command_name) + '\n')
    fout.write("""\\end{reftable}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Test code for fine-tuning the new commands
""")

    for command_name in latex_cmds:
        for line in latex_cmds[command_name][1]:
            fout.write(line)

    fout.write('\\end{document}\n')
    fout.close()

def write_lily_src_files():
    for command_name in lily_cmds:
        print '- ' + command_name
        # open a single lily src file for write access
        fout = open('generated_src/' + command_name + '.ly',  'w')

        #output the license information
        fout.write(lilyglyphs_copyright_string)
        fout.write('\n')

        #output information on the actual file
        write_file_info(command_name, fout)

        #write the default LilyPond stuff
        fout.write(lily_src_prefix)

        # write the comment for the command
        fout.write('%{\n')
        for line in lily_cmds[command_name][0]:
            fout.write(line + '\n')
        fout.write('%}\n\n')

        # write the actual command
        fout.write(command_name + ' = {\n')
        for line in lily_cmds[command_name][1]:
            fout.write(line + '\n')
        fout.write('}\n')

        # write the score definition
        fout.write(lily_src_score)

        # finish the LilyPond file
        fout.write('  \\' + command_name + '\n')
        fout.write('}\n\n')

        fout.close()

# ####################################
# Finally launch the program
if __name__ == "__main__":
    main(sys.argv[1:])