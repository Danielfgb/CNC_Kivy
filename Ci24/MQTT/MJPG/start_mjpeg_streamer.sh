#!/bin/bash

# Inicia el streamer en el puerto 8080
mjpg_streamer -i "/usr/lib/input_uvc.so" -o "/usr/lib/output_http.so -w /usr/share/mjpg-streamer/www" -p 8080
