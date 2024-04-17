{ pkgs, ... }: {
  deps = [
    pkgs.run
    pkgs.ffmpeg
    pkgs.libopus
    pkgs.ffmpeg.bin
  ];

  # Asegúrate de que el entorno de Python pueda encontrar libopus
  PYTHON_LD_LIBRARY_PATH = "${pkgs.libopus}/lib";
}
