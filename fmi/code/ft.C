#include <iomanip>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <errno.h>
#include <assert.h>
#include <string.h>
#include <time.h>
#include "variables.H"
#include "gridcache.H"
#define MAX_VARS 1000

struct Xcoord
{
  double x;
  double y;
  double z;
};

struct Box
{
  struct Xcoord bmin;
  struct Xcoord bmax;
  double radius;
};

void die(const char *message)
{
  if(errno) {
    perror(message);
  } else {
    printf("ERROR: %s\n", message); // TODO -> print in the error
  }
  exit(1);
}

char *buildvarlist(char *var_input)
{
  static char result[MAX_VARS];
  char axis[3] = {'x', 'y', 'z'};
  int i = 0;
  int j = 0;
  int k = 0;
  if(!strcmp(var_input,"B0") || !strcmp(var_input,"B1")) {
    for(i = 0; i < 3; i++) {
      result[k++] = var_input[0];
      result[k++] = axis[i];
      result[k++] = var_input[1];
      if(i != 2) result[k++] = ',';
    }
  } else {
    for(i = 0; i < 3; i++) {
      for(j = 0; j < strlen(var_input); j++) {
	result[k++] = var_input[j];
      }
      result[k++] = axis[i];
      if(i != 2) result[k++] = ',';
    }
  }
  result[k] = '\0';
  return result;

}

int *variablesMask(int nvarnames, char *varnames[], char *VariableList)
{
  /** 
   * Used to get from an input string like: "rho,B0,B1" (VariableList)
   * the amount and the original order of these variables
   * on the input variables list (varnames)
   * 
   * If exits if not variable matches. It throw warnings 
   * for variables that are not found.
   */
  
  // find number of variables separated by commas
  int ntokens = 1;
  // find the position of the commas
  int commapos[MAX_VARS];
  int i = 0, j = 0;
  for(i=0; VariableList[i]; i++){
    if(VariableList[i] == ','){
      ntokens++;
      commapos[j++] = i;
    }
  }
  // Find start and end of the comma positions to extract variables
  int tok_start[MAX_VARS], tok_end[MAX_VARS];
  tok_start[0] = 0;
  for(i = 0; i < ntokens-1; i++) {
    tok_start[i+1] = commapos[i]+1;
    tok_end[i] = commapos[i]-1;
  }
  tok_end[ntokens-1] = strlen(VariableList)-1;
  
  // check variables exist and find their position.
  char ss[MAX_VARS];
  //bool errors = false;
  static int varpos[MAX_VARS];
  
  int numbers[MAX_VARS+1];
  numbers[0] = 0;
  for(i = 0; i < MAX_VARS; i++) numbers[i+1] = i;
  
  memcpy(varpos, numbers, MAX_VARS * sizeof(int));
  varpos[0] = 0;
  for(i = 0; i < ntokens; i++){
    int k = 0;
    for(j = tok_start[i]; j<=tok_end[i]; j++) ss[k++] = VariableList[j];
    ss[k] = '\0';
    for(j = 0; j < nvarnames; j++){
      if(!strcmp(varnames[j], ss)){
	varpos[varpos[0]+1] = j;
	varpos[0]++;
	break;
      } 
    }
    if(varpos[0] != i+1) printf("Variable %s not recognize\n", ss);
    
    
    //      if(!found) errmsg("Unrecognized variable name %s ", ss)
  }
  
  if(!varpos[0]) die("Unrecognized variable");
  return varpos;
}


struct Xcoord normal_vector(struct Xcoord X)
{
  double modulus;
  modulus = sqrt((X.x * X.x) + (X.y * X.y) + (X.z * X.z));
  if(modulus == 0) {
    die("Bad vector");
  } else {
    X.x /= modulus;
    X.y /= modulus;
    X.z /= modulus;
  } 
  return X;    
}

struct Xcoord follow_point(
			   struct Xcoord X0, 
			   struct Xcoord field, 
			   //struct Xcoord field,
			   int stepsize)
{
  struct Xcoord pout;
  
  field = normal_vector(field);

  pout.x = X0.x + (field.x * stepsize);
  pout.y = X0.y + (field.y * stepsize);
  pout.z = X0.z + (field.z * stepsize);

  return pout;
}

int withinbox(struct Xcoord X, 
	      struct Box Box)
{
  if(X.x < Box.bmin.x || X.x > Box.bmax.x) return 0;
  if(X.y < Box.bmin.y || X.y > Box.bmax.y) return 0;
  if(X.z < Box.bmin.z || X.z > Box.bmax.z) return 0;
  if(sqrt((X.x * X.x)+(X.y * X.y)+(X.z * X.z)) < Box.radius) return 0;
  //printf("Radius = %g\n", sqrt((X.x * X.x)+(X.y * X.y)+(X.z * X.z)));
  return 1;
}

void midpoint(struct Xcoord X0, struct Box Box)
{
  // start point 0; 
  // inside box?
  if(!withinbox(X0, Box)) die("Points outside boundaries");
  printf("It seems working so far\n");
  // get field value

  // get mp and 
  // inside box?
  // get field value for mp

  // get final point

  // inside box?
  // return value
}


int main(int argc, char *argv[])
{

  // set input starting point  // read from argv
  struct Xcoord p0 = {.x = 3000000, .y = 0, .z = 0};

  // set input starting box  // read from argv
  struct Xcoord xmin = {.x = -30000000, .y = -300000000, .z = -300000000};
  struct Xcoord xmax = {.x = 30000000, .y = 30000000, .z = 30000000};
  struct Box boxy = { .bmin = xmin, .bmax = xmax, .radius = 1};

  // set input variable; from B to Bx, By, Bz
  char *var_input = "j"; // read from argv
  char *varlist = 0;

  varlist = buildvarlist(var_input);
  char *varnames[MAX_VARS];   /*= {"rho", "B0", "B1", "n", "A", "B",
			      "Bx0", "Bx1", "By0", "By1", "Bz0",
			      "Bz1", "rhovx", "rhovy", "rhoz"}; */
  int i, j;
  
  Tvariable var; 
  int nvarnames = var.Nvars();
  for(i = 0; i < nvarnames; i++) {
    var.select(i); 
    varnames[i] = strdup(var.selected());
  }
  
  int *varpos = variablesMask(nvarnames, varnames, varlist);

  printf("varpos[0] = %d\n", varpos[0]);
  for(i = 1; i <= varpos[0]; i++){
    printf("%s was asked as %d and it has position %d\n", varnames[varpos[i]], i, varpos[i]);
  }
  
  if(varpos[0] != 3) die("You've got more or less variables than needed");
  
  // READ file
  char *hcfile = "/home/perezsua/H+_hybstate_00575000.hc";
  TGridCache gridcache;
  double Gamma, Invmu0, Mass;
  bool Pseudobackground;
  Tmetagrid* gp = gridcache.open(hcfile,Gamma,Invmu0,Mass,Pseudobackground);
  if (!gp) die("cannot open HC file ");
  Tmetagrid& g = *gp;

  // Update box
  double amin[3], amax[3];
  g.getbox(amin, amax);
  if(boxy.bmin.x > amin[0]) boxy.bmin.x = amin[0];
  if(boxy.bmin.y > amin[1]) boxy.bmin.y = amin[1];
  if(boxy.bmin.z > amin[2]) boxy.bmin.z = amin[2];
  if(boxy.bmax.x > amax[0]) boxy.bmax.x = amax[0];
  if(boxy.bmax.y > amax[1]) boxy.bmax.y = amax[1];
  if(boxy.bmax.z > amax[2]) boxy.bmax.z = amax[2];


  int max_points = 400; //TODO: needs to be read from argv
  double step = 40000; // TODO: needs to be read from argv
  /* TODO: if backward -> step = -step */

  double field_a[3];
  struct Xcoord field;
  struct Xcoord mp;

  // start point 0; 
  // inside box?
  if(!withinbox(p0, boxy)) die("Points outside boundaries");
  printf("%g %g %g\n",p0.x, p0.y, p0.z);

  for(i = 0; i <= max_points; i++) {
    //printf("It seems working so far\n");
    // get field value
    Tdimvec X(p0.x, p0.y, p0.z);
    for(j = 1; j <= varpos[0]; j++){
      if(!g.intpol(X, 1, true)) { /* TODO: add order from linear or not */
	die("the point is wrong");
      } else {
	var.select(varnames[varpos[j]], Gamma, Invmu0, Mass);
	field_a[j-1] = var.get(g, X);
      }
    }
    field = {.x = field_a[0], .y = field_a[1], .z = field_a[2]};
    
    // get mp and 
    mp = follow_point(p0, field, step/2);
    // inside box?
    if(!withinbox(p0, boxy)) die("Points outside boundaries");
    // get field value for mp
    Tdimvec Y(mp.x, mp.y, mp.z);
    for(j = 1; j <= varpos[0]; j++){
      if(!g.intpol(Y, 1, true)) {
	die("the point is wrong");
      } else {
	var.select(varnames[varpos[j]], Gamma, Invmu0, Mass);
	field_a[j-1] = var.get(g, Y);
      }
    }
    field = {.x = field_a[0], .y = field_a[1], .z = field_a[2]};

    // get final point
    p0 = follow_point(p0, field, step);

    // inside box?
    if(!withinbox(p0, boxy)) die("Points outside boundaries");
    // print value
    printf("%g %g %g\n",p0.x, p0.y, p0.z);
  }

  return 0;


}
