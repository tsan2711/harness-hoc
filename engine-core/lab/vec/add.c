void add_may_alias(float *pos, const float *vel, float dt, int n){ for(int i=0;i<n;i++) pos[i]+=vel[i]*dt; }
void add_noalias(float *restrict pos, const float *restrict vel, float dt, int n){ for(int i=0;i<n;i++) pos[i]+=vel[i]*dt; }
float sum_strict(const float *a,int n){ float s=0; for(int i=0;i<n;i++) s+=a[i]; return s; }
float sum_reassoc(const float *a,int n){
#pragma clang fp reassociate(on)
 float s=0; for(int i=0;i<n;i++) s+=a[i]; return s; }
void gather(float *restrict o,const float *restrict a,const int *restrict idx,int n){ for(int i=0;i<n;i++) o[i]=a[idx[i]]*2; }
