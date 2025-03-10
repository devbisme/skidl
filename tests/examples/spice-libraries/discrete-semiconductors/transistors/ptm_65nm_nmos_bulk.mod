* Customized PTM 65nm NMOS
*
* This file has been downloaded from the
* Predictive Technology Model (PTM) website
* http://ptm.asu.edu/
* using the "Nano-CMOS" form and using the default values.
*
* It has been slightly modified from its original for compliance
* reasons with the PySpice python module
* (renamed and cleaned of invisible characters causing errors)
* Please refer to the PTM website and the related publications
* for more information about the technology.
*
* This file is provided here for educational purpose
*

.model  ptm65nm_nmos  nmos  level = 54

+version = 4.0    binunit = 1    paramchk= 1    mobmod  = 0
+capmod  = 2      igcmod  = 1    igbmod  = 1    geomod  = 1
+diomod  = 1      rdsmod  = 0    rbodymod= 1    rgatemod= 1
+permod  = 1      acnqsmod= 0    trnqsmod= 0

* parameters related to the technology node
+tnom = 27          epsrox  = 3.9
+eta0 = 0.0058      nfactor = 1.9           wint = 5e-09
+cgso = 1.5e-10     cgdo    = 1.5e-10       xl   = -3e-08

* parameters customized by the user
+toxe = 1.85e-09    toxp = 1.2e-09      toxm = 1.85e-09     toxref = 1.85e-09
+dtox = 6.5e-10     lint = 5.25e-09
+vth0 = 0.429       k1   = 0.497        u0   = 0.04861      vsat   = 124340
+rdsw = 165         ndep = 2.6e+18      xj   = 1.96e-08

* secondary parameters
+ll      = 0            wl      = 0            lln     = 1            wln     = 1
+lw      = 0            ww      = 0            lwn     = 1            wwn     = 1
+lwl     = 0            wwl     = 0            xpart   = 0
+k2      = 0.01         k3      = 0
+k3b     = 0            w0      = 2.5e-006     dvt0    = 1            dvt1    = 2
+dvt2    = -0.032       dvt0w   = 0            dvt1w   = 0            dvt2w   = 0
+dsub    = 0.1          minv    = 0.05         voffl   = 0            dvtp0   = 1.0e-009
+dvtp1   = 0.1          lpe0    = 0            lpeb    = 0
+ngate   = 2e+020       nsd     = 2e+020       phin    = 0
+cdsc    = 0.000        cdscb   = 0            cdscd   = 0            cit     = 0
+voff    = -0.13        etab    = 0
+vfb     = -0.55        ua      = 6e-010       ub      = 1.2e-018
+uc      = 0            a0      = 1.0          ags     = 1e-020
+a1      = 0            a2      = 1.0          b0      = 0            b1      = 0
+keta    = 0.04         dwg     = 0            dwb     = 0            pclm    = 0.04
+pdiblc1 = 0.001        pdiblc2 = 0.001        pdiblcb = -0.005       drout   = 0.5
+pvag    = 1e-020       delta   = 0.01         pscbe1  = 8.14e+008    pscbe2  = 1e-007
+fprout  = 0.2          pdits   = 0.08         pditsd  = 0.23         pditsl  = 2.3e+006
+rsh     = 5            rsw     = 85           rdw     = 85
+rdswmin = 0            rdwmin  = 0            rswmin  = 0            prwg    = 0
+prwb    = 6.8e-011     wr      = 1            alpha0  = 0.074        alpha1  = 0.005
+beta0   = 30           agidl   = 0.0002       bgidl   = 2.1e+009     cgidl   = 0.0002
+egidl   = 0.8

+aigbacc = 0.012        bigbacc = 0.0028       cigbacc = 0.002
+nigbacc = 1            aigbinv = 0.014        bigbinv = 0.004        cigbinv = 0.004
+eigbinv = 1.1          nigbinv = 3            aigc    = 0.012        bigc    = 0.0028
+cigc    = 0.002        aigsd   = 0.012        bigsd   = 0.0028       cigsd   = 0.002
+nigc    = 1            poxedge = 1            pigcd   = 1            ntox    = 1

+xrcrg1  = 12           xrcrg2  = 5
+cgbo    = 2.56e-011    cgdl    = 2.653e-10
+cgsl    = 2.653e-10    ckappas = 0.03         ckappad = 0.03         acde    = 1
+moin    = 15           noff    = 0.9          voffcv  = 0.02

+kt1     = -0.11        kt1l    = 0            kt2     = 0.022        ute     = -1.5
+ua1     = 4.31e-009    ub1     = 7.61e-018    uc1     = -5.6e-011    prt     = 0
+at      = 33000

+fnoimod = 1            tnoimod = 0

+jss     = 0.0001       jsws    = 1e-011       jswgs   = 1e-010       njs     = 1
+ijthsfwd= 0.01         ijthsrev= 0.001        bvs     = 10           xjbvs   = 1
+jsd     = 0.0001       jswd    = 1e-011       jswgd   = 1e-010       njd     = 1
+ijthdfwd= 0.01         ijthdrev= 0.001        bvd     = 10           xjbvd   = 1
+pbs     = 1            cjs     = 0.0005       mjs     = 0.5          pbsws   = 1
+cjsws   = 5e-010       mjsws   = 0.33         pbswgs  = 1            cjswgs  = 3e-010
+mjswgs  = 0.33         pbd     = 1            cjd     = 0.0005       mjd     = 0.5
+pbswd   = 1            cjswd   = 5e-010       mjswd   = 0.33         pbswgd  = 1
+cjswgd  = 5e-010       mjswgd  = 0.33         tpb     = 0.005        tcj     = 0.001
+tpbsw   = 0.005        tcjsw   = 0.001        tpbswg  = 0.005        tcjswg  = 0.001
+xtis    = 3            xtid    = 3

+dmcg    = 0e-006       dmci    = 0e-006       dmdg    = 0e-006       dmcgt   = 0e-007
+dwj     = 0.0e-008     xgw     = 0e-007       xgl     = 0e-008

+rshg    = 0.4          gbmin   = 1e-010       rbpb    = 5            rbpd    = 15
+rbps    = 15           rbdb    = 15           rbsb    = 15           ngcon   = 1
