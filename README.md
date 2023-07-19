# thirdpartygenerator

## Requirements

- [pkgname_analyzer](https://github.com/amdslancelot/pkgname_analyzer)
```
export PYTHONPATH="/root/git/pkgname_analyzer/"
```

## Usage
```
# /root/git/thirdpartygenerator/third_party_generator.py -h
usage: third_party_generator.py [-h] [--package PACKAGE] [--prefix PREFIX]
                                [--filter FILTER] [-d]

Lans License File Detect Tool

optional arguments:
  -h, --help            show this help message and exit
  --package PACKAGE, -p PACKAGE
                        looking for specific package
  --prefix PREFIX, -pf PREFIX
                        A prefix in the file to remove
  --filter FILTER, -fi FILTER
                        A filter(also a prefix) to move the preferred pkg name
                        (starts with the filter prefix) to be picked up first
  -d, --debug           debug mode
```

## Example: Generate 3rd party license for `python39-click`
```
# ./third_party_generator.py -p click -pf python- -fi python39- 
===============================================================================

                  LICENSES FOR THIRD-PARTY COMPONENTS

===============================================================================

----------------------------------------------------------
python-importlib-metadata 4.10.1 (Apache Software License)
----------------------------------------------------------


Copyright 2017-2019 Jason R. Coombs, Barry Warsaw

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

================================================================================

---------------------------
python-colorama 0.4.4 (BSD)
---------------------------


Copyright (c) 2010 Jonathan Hartley
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holders, nor those of its contributors
  may be used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

================================================================================
```

## Debug
```
# ./third_party_generator.py -p click -pf python- -fi python39- -d
```
