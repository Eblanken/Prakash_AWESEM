#
# File: AWESEM_InstallScript.py
# ------------------------------
# Authors: Erick Blankenberg
# Date: 12/2/2018
#
# Description:
#   This script loads all of the packages not already included in Anaconda
#   NOTE: Please run me as an administrator!
#

import conda.cli

conda.cli.main('conda', 'install',  '-y', 'pyserial')
conda.cli.main('conda' 'install' 'numpy-indexed' '-c' 'conda-forge')
