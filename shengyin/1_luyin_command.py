arecord -D dmic_sv -c2 -r 48000 -f S32_LE -t wav -V mono | cvlc -vvv stream:///dev/stdin --sout '#transcode{acodec=mp2,ab=128):rtp{sdp=rtsp://:8554/}'
sudo systemctl enable audiostream^C
sudo nano /etc/dhcpcd.conf
sudo raspi-config
cat audiostream.py

SERVER_IP = "192.168.10.11"
SERVER_PORT = 8554
STREAM_VLC_CMD = "/usr/bin/arecord -D dmic_sv -c2 -r 48000 -f S32_LE -t wav -V mono | avconv -i - -acodec libmp3lame -b 32k -f rtp rtp://{}:{}/4".format(CLIENT_IP,CLIENT_PORT)"
STREAM_VLC_CMD = "/usr/bin/arecord -D dmic_sv -c2 -r 48000 -f S32_LE -t wav -V mono | cvlc -vvv stream:///dev/stdin --sout '#transcode(acodec=mp2,ab=128):rtp{sdp=rtsp://:8554/}'"os.system(STREAM_VLC_CMD)
