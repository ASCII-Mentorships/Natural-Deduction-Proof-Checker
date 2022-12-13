# Makefile for ndp_parser

# define the target
cmd_name: ndp_parser

# download the required libraries
down: pip install sly
        pip install auto-py-to-exe

# compile the ndp_parser script into an executable
comp: auto-py-to-exe ndp_parser.py

# rename the executable and move it to the output directory
ren: mv ndp_parser.exe output/ndp_parser/natded

# add the output directory to the system path
ex: export PATH=$PATH:./output/ndp_parser
