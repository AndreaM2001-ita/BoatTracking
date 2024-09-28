Setting up the environment
Install Anaconda
In Anaconda type:
Conda create -n *NAME* python=3.10
Y
Conda activate *NAME*
Pip install ultralytics
Download this file:
https://www.dllme.com/dll/files/libomp140_x86_64?sort=upload&arch=0x8664
Unzip libomp140…. Dll into the same directory as fbgemm.dll
(C:\Users\*USER*\anaconda3\envs\*****\Lib\site-packages\torch\lib)
where ***** is the name of your environment
Copy this whole command, URL included, into anaconda and run:
If you have a nVidia graphics card, do this next step, otherwise, skip it
pip3 install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install EasyDict

Install Git
Once Git is installed, close the Boat Tracking repo to create a working directory:
Git clone https://github.com/AndreaM2001-ita/BoatTracking.git
Go into the Boat Tracking folder (in anaconda) and then clone the Deep Sort repo:
Git clone https://github.com/AarohiSingla/Tracking-and-counting-Using-YOLOv8-and-DeepSORT.git

Once the deep sort repo is cloned, you’ll need to copy the Tracker.py file from the BoatTracking folder into deep_sort/sort/
This will overwrite the existing one


That should do it…
