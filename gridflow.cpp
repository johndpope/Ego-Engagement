#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>

#define TAG_FLOAT 202021.25  // check for this when READING the file

int xgrid, ygrid, dngrid;

void ReadFlowFile(const char *filename, float *averageflow) {
  FILE *stream = fopen(filename, "rb");

  int width, height;
  float tag;
  fread(&tag, sizeof(float), 1, stream);
  fread(&width,  sizeof(int), 1, stream);
  fread(&height, sizeof(int), 1, stream);
  if (tag != TAG_FLOAT) {
    fprintf(stderr, "Wrong format in %s\n", filename);
    exit(1);
  }
  int n_pixels = width * height;

  float flow[2];
  int gridwidth = (width-1) / xgrid + 1;
  int gridheight = (height-1) / ygrid + 1;
  int gridsize = gridwidth * gridheight;

  memset(averageflow, 0, sizeof(float)*dngrid);
  for (int i=0; i<n_pixels; i++) {
    fread(flow, sizeof(float), 2, stream);
    int x_cord = i % width;
    int y_cord = i / width;
    int grid_x = x_cord / gridwidth;
    int grid_y = y_cord / gridheight;

    averageflow[2*(grid_y*xgrid + grid_x)] += flow[0] / gridsize;
    averageflow[2*(grid_y*xgrid + grid_x)+1] += flow[1] / gridsize;
  }
  fclose(stream);
}

int main(int argc, char **argv) {
  std::ifstream infile(argv[1]);
  xgrid = atoi(argv[2]);
  ygrid = atoi(argv[3]);
  dngrid = 2 * xgrid * ygrid;

  if (infile) {
    std::string line;
    float averageflow[dngrid];
    while (getline(infile, line)) {
      ReadFlowFile(line.c_str(), averageflow);
      fprintf(stdout, "%s", line.c_str());
      for (int i=0; i<dngrid; i++) {
        fprintf(stdout, " %f", averageflow[i]);
      }
      fprintf(stdout, "\n");
    }
  }
  infile.close();

  return 0;
}
