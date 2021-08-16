 docker pull mdegans/tegra-opencv

// this is lightweight docker file, with only  1.41GB
as tag is not here so it will automatically donwload latest version


docker pull dustynv/jetson-inference:r32.4.4
// this image contains tensorRT as well so it more fast, but image size is 3.11GB

how to run the code

go into interactive mode, incase you cant go, please contact shanullah 

then  copy the files
sudo docker cp Hostpath conainter_ID: container_path

python3 Object_DetectionShan_SSDMobileNetver3.py

python3 Object_DetectionShan_TinyYolover4.py

good to go

