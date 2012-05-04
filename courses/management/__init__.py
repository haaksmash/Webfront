from ..models import GradYear,Campus,Building,Utility,\
                           Major, Course, Department,\
                           MajorCourseRequirement, Prerequisite, Day, Semester
from .. import models as features
from django.db.models import signals

import datetime

def create_requirements(course_list, major,**kwargs):
    for course in course_list:
        if type(course) is tuple:
            if kwargs['verbosity'] > 2: print "\t\tAssigning alternate course for {}: {}".format(course[0],course[1])
            # this is a set of exchangeable courses.
            c, new = MajorCourseRequirement.objects.get_or_create(
                         major=major,
                         course=course[0],
                         )
            for alt in course[1:]:
                c.alternates.add(alt)
            c.save()
        else:
            if kwargs['verbosity'] > 2: print "\t\tAssigning {} to core".format(course)
            c, new = MajorCourseRequirement.objects.get_or_create(
                        major=major,
                        course=course
                        )

""" The following methods are attached to the post_syncdb signal
and are used to ensure that certain objects never need to be created 
on the fly."""
def prepopulate_days(sender, **kwargs):
    """Creates the seven day objects"""
    if not kwargs.has_key('verbosity'):
        kwargs['verbosity'] = 0
    if kwargs['verbosity'] > 0: print "Creating days of the week"
    for (code, name) in Day.DAY_CHOICES:
        if code not in ['T', 'W','R']:
            short = name[:3]
        elif code in ['T', 'R']:
            short = name[:-3]
        elif code == 'W':
            short = "Weds"
        if kwargs['verbosity'] > 1: print "\tCreating {}".format(name)
        Day.objects.get_or_create(name=name,
                                  code=code,
                                  short=short)
signals.post_syncdb.connect(prepopulate_days, sender=features)

def prepopulate_semesters(sender, **kwargs):
    """Creates semesterly objects."""
    if not kwargs.has_key('verbosity'):
        kwargs['verbosity'] = 0
    if kwargs['verbosity'] > 0: print "Creating semester objects"
    for year in range(datetime.datetime.now().year-4, datetime.datetime.now().year+2):
        fa, new = Semester.objects.get_or_create(year=year,
                                                 half='FA')
        sp, new = Semester.objects.get_or_create(year=year,
                                                 half='SP')
        sm, new = Semester.objects.get_or_create(year=year,
                                                 half='SM')
    
signals.post_syncdb.connect(prepopulate_semesters, sender=features)

def prepopulate_campuses(sender,**kwargs):
    """ Create objects for the campuses if they don't exist"""
    if not kwargs.has_key('verbosity'):
        kwargs['verbosity'] = 0
    for pair in Campus.CAMPUSES:
        if kwargs['verbosity'] > 0:
            print "Creating campus {}".format(pair[0])
        c, new = Campus.objects.get_or_create(code=pair[0])
        c.title = pair[1] # update title if necessary
        c.save()
signals.post_syncdb.connect(prepopulate_campuses, sender=features)

def prepopulate_buildings(sender, **kwargs):
    """Create objects for buildings automatically"""
    if not kwargs.has_key('verbosity'):
        kwargs['verbosity'] = 0
    for campus in Building.BUILDINGS:
        c = Campus.objects.get(code=campus[0])
        if kwargs['verbosity'] > 0:
            print "Creating buildings for campus: {}".format(c)
        for building in campus[1]:
            if kwargs['verbosity'] > 1:
                print "\t Creating building: {}".format(building[0])  
            b, new = Building.objects.get_or_create(campus=c,
                                           code=building[0])
            b.name = building[1]
            b.save()
signals.post_syncdb.connect(prepopulate_buildings, sender=features)

def prepopulate_gradyears(sender, **kwargs):
    """Create graduation years"""
    if not kwargs.has_key('verbosity'):
        kwargs['verbosity'] = 0
    if kwargs['verbosity'] > 0: print "Creating possible GradYears"
    for year in Utility().possible_grad_years():
        if kwargs['verbosity'] > 1: print "\tCreating GradYear:{}".format(year)
        y, new = GradYear.objects.get_or_create(year=year)
signals.post_syncdb.connect(prepopulate_gradyears, sender=features)

def prepopulate_core(sender, **kwargs):
    """Creates the HMC Core requirements as a major, to which all HMC students
    should be automatically added."""
    if not kwargs.has_key('verbosity'):
        kwargs['verbosity'] = 0
    if kwargs['verbosity'] > 0: print "Creating HMC Core requirements"
    core = []
    hmc, new = Campus.objects.get_or_create(code='HM') # should have been created already
    
    if kwargs['verbosity'] > 1: print "\tCreating HM Engineering Dept."
    engr, new = Department.objects.get_or_create(
                     name="Engineering",
                     code="ENGR",
                     campus=hmc,
                     )
    if kwargs['verbosity'] > 2: print "\t\tCreating ENGR59"
    engr59, new = Course.objects.get_or_create(
                    title="Introduction to Engineering Systems",
                    department=engr,
                    codenumber="59",
                    campus=hmc,
                    description="""An introduction to the concepts of modern engineering, 
                    emphasizing modeling, analysis, synthesis and design. 
                    Applications to chemical, mechanical and electrical systems. 
                    Prerequisite: sophomore standing. Corequisite: 
                    Physics 51. 3 credit hours. (Fall and Spring.)"""
                    )
    core += [engr59]
    
    if kwargs['verbosity'] > 1: print "\tCreating HM Chemistry Dept."
    chem, new = Department.objects.get_or_create(
                     name="Chemistry",
                     code="CHEM",
                     campus=hmc,
                     
                     )
    if kwargs['verbosity'] > 2: print "\t\tCreating CHEM23D"
    chem23d, new = Course.objects.get_or_create(
                    title="Dynamics",
                    department=chem,
                    codenumber="23D",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating CHEM23E"
    chem23e, new = Course.objects.get_or_create(
                    title="Energetics",
                    department=chem,
                    codenumber="23E",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating CHEM23S"
    chem23s, new = Course.objects.get_or_create(
                    title="Structure",
                    department=chem,
                    codenumber="23S",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating CHEM24"
    chem24, new = Course.objects.get_or_create(
                    title="Chemistry Laboratory",
                    department=chem,
                    codenumber="24",
                    campus=hmc,
                    credit_hours=1.00,
                    classtype='B'
                    )
    core += [chem23d,chem23e,chem23s,chem24]
    
    if kwargs['verbosity'] > 1: print "\tCreating HM Physics Dept."
    phys, new = Department.objects.get_or_create(
                     name="Physics",
                     code="PHYS",
                     campus=hmc,
                     )
    if kwargs['verbosity'] > 2: print "\t\tCreating PHYS22"
    phys22, new = Course.objects.get_or_create(
                    title="Physics Laboratory",
                    department=phys,
                    codenumber="22",
                    campus=hmc,
                    credit_hours=1.00,
                    classtype='B'
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating PHYS23"
    phys23, new = Course.objects.get_or_create(
                    title="Special Relativity",
                    department=phys,
                    codenumber="23",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating PHYS24"
    phys24, new = Course.objects.get_or_create(
                    title="Mechanics & Wave Motion",
                    department=phys,
                    codenumber="24",
                    campus=hmc,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating PHYS51"
    phys51, new = Course.objects.get_or_create(
                    title="Electromagnetic Theory & Optics",
                    department=phys,
                    codenumber="51",
                    campus=hmc,
                    )
    req = Prerequisite.objects.get_or_create(course=phys51, requisite=phys23)
    req = Prerequisite.objects.get_or_create(course=phys51, requisite=phys24)
    engr59.concurrent_with.add(phys51)
    core += [phys22,phys23,phys24,phys51]
    if kwargs['verbosity'] > 1: print "\tCreating HM CompSci Dept."
    csci, new = Department.objects.get_or_create(
                     name="Computer Science",
                     code="CSCI",
                     campus=hmc,
                     )
    if kwargs['verbosity'] > 2: print "\t\tCreating CSCI5 gold"
    csci5g, new = Course.objects.get_or_create(
                    title="Introduction to Computer Science",
                    department=csci,
                    codenumber="5G",
                    campus=hmc,
                    )
    csci5b, new = Course.objects.get_or_create(
                   title="Introduction to Computer Science",
                   department=csci,
                   codenumber="5G",
                   campus=hmc,                            
                   )
    csci5l, new = Course.objects.get_or_create(
                   title="Intro to Computer Science Lab",
                   department=csci,
                   codenumber="5L",
                   campus=hmc,
                   classtype='B',
                   credit_hours=0.00,
                   )
    csci5b.concurrent_with.add(csci5l)
    csci5g.concurrent_with.add(csci5l)
    
    csci5gr, new = Course.objects.get_or_create(
                    title="Intro to Biology and Computer Science",
                    department=csci,
                    codenumber="5GR",
                    campus=hmc                            
                    )
    csci5grl, new = Course.objects.get_or_create(
                    title="Intro Biol and Computer Sci Lab",
                    department=csci,
                    codenumber="5GL",
                    campus=hmc,
                    classtype='B',
                    credit_hours=0.00,
                    )
    csci5gr.concurrent_with.add(csci5grl)
    
    if kwargs['verbosity'] > 2: print "\t\tCreating CSCI42"
    csci42, new = Course.objects.get_or_create(
                    title="Principles & Practice: Comp Sci",
                    department=csci,
                    codenumber="42",
                    campus=hmc,
                    )
    core += [(csci5g, csci5b, csci5gr, csci42)]
    
    if kwargs['verbosity'] > 1: print "\tCreating HM Math Dept."
    math, new = Department.objects.get_or_create(
                     name="Mathematics",
                     code="MATH",
                     campus=hmc,
                     )
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH30B"
    math30b, new = Course.objects.get_or_create(
                    title="Calculus",
                    department=math,
                    codenumber="30B",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH30G"
    math30g, new = Course.objects.get_or_create(
                    title="Calculus",
                    department=math,
                    codenumber="30G",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH35"
    math35, new = Course.objects.get_or_create(
                    title="Probability and Statistics",
                    department=math,
                    codenumber="35",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH40"
    math40, new = Course.objects.get_or_create(
                    title="Intro to Linear Algebra",
                    department=math,
                    codenumber="40",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH45"
    math45, new = Course.objects.get_or_create(
                    title="Intro to Differential Equations",
                    department=math,
                    codenumber="45",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH60"
    math60, new = Course.objects.get_or_create(
                    title="Multivariable Calculus",
                    department=math,
                    codenumber="60",
                    campus=hmc,
                    credit_hours=1.5,
                    )    
    if kwargs['verbosity'] > 2: print "\t\tCreating MATH65"
    math65, new = Course.objects.get_or_create(
                    title="Differential Eqns/Linear Alg II",
                    department=math,
                    codenumber="65",
                    campus=hmc,
                    credit_hours=1.5,
                    )
    
    phys51.concurrent_with.add(math60)
    core += [(math30b, math30g), math35, math40, math45,math60,math65]
    
    if kwargs['verbosity'] > 1: print "\tCreating HM Biology Dept."
    biol, new = Department.objects.get_or_create(
                     name="Biology",
                     code="BIOL",
                     campus=hmc,
                     )
    if kwargs['verbosity'] > 2: print "\t\tCreating BIOL52"
    biol52, new = Course.objects.get_or_create(
                    title="Introduction to Biology",
                    department=biol,
                    codenumber="52",
                    campus=hmc,
                    )
    core += [(biol52,csci5gr)]
    
    if kwargs['verbosity'] > 1: print "\tCreating Choice Lab department"
    cl, new = Department.objects.get_or_create(
                    name="Choice Lab",
                    code="CL",
                    campus=hmc,
                    )
    if kwargs['verbosity'] > 2: print "\t\tCreating CL057"
    cl57, new = Course.objects.get_or_create(
                     title="Choice Lab",
                     department=cl,
                     codenumber="57",
                     campus=hmc
                     )
    core += [cl57]
    
    
    if kwargs['verbosity'] > 1: print "\t\tCreating HMC Humanities Dept."
    coredept, new = Department.objects.get_or_create(
                     name="Humanities",
                     code="HUM",
                     campus=hmc
                     )
    
    if kwargs['verbosity'] > 1: print "\t\tCreating HMC Writing Dept."
    hmcwrit, new = Department.objects.get_or_create(
                    name="Writing",
                    code="WRIT",
                    campus=hmc
                    )
    
    writ1 = Course.objects.get_or_create(
                     title="Introduction to Academic Writing",
                     department=hmcwrit,
                     codenumber="1",
                     campus=hmc
                     )
    if kwargs['verbosity'] > 0: print "\tCreating HMC Core major"
    hmcore, new = Major.objects.get_or_create(title="HMC Core")
    hmcore.departments.add(coredept)
    if kwargs['verbosity'] > 1: print "\tAttaching courses to Core major"
    create_requirements(core, hmcore, **kwargs)
#signals.post_syncdb.connect(prepopulate_core, sender=features)   

def create_major_HM_CSCI(**kwargs):
    hmc = Campus.objects.get(code="HM")
    csci = Department.objects.get(code="CSCI", campus=hmc)
    math = Department.objects.get(code="MATH", campus=hmc)
    cs60, new = Course.objects.get_or_create(
                 title="Principles of Computer Science",
                 codenumber="60",
                 department=csci,
                 campus=hmc,
                )
    cs70, new = Course.objects.get_or_create(
                 title="Data Structures and Program Development",
                 codenumber="70",
                 department=csci,
                 campus=hmc,
                )
    cs81, new = Course.objects.get_or_create(
                 title="Computability and Logic",
                 codenumber="81",
                 department=csci,
                 campus=hmc,
                )
    cs105, new = Course.objects.get_or_create(
                 title="Computer Systems",
                 codenumber="105",
                 department=csci,
                 campus=hmc,
                )
    cs121, new = Course.objects.get_or_create(
                 title="Software Development",
                 codenumber="121",
                 department=csci,
                 campus=hmc,
                )
    cs131, new = Course.objects.get_or_create(
                 title="Programming Languages",
                 codenumber="131",
                 department=csci,
                 campus=hmc,
                )
    cs140, new = Course.objects.get_or_create(
                 title="Algorithms",
                 codenumber="140",
                 department=csci,
                 campus=hmc,
                )
    
    math55, new = Course.objects.get_or_create(
                 title="Discrete Mathematics",
                 codenumber="55",
                 department=math,
                 campus=hmc,
                )
    cs42 = Course.objects.get(codenumber=42, department=csci)
    cs5s = Course.objects.filter(number=5, department=csci, classtype__in=["L","S"])
    
    cp, new = Prerequisite.objects.get_or_create(
               course=cs60,
               requisite=cs5s[0],
               )
    cp.alternates = cs5s[1:]
    cp, new = Prerequisite.objects.get_or_create(
               course=cs70,
               requisite=cs60,
               )
    cp.alternates = cs5s[1:]
    cp, new = Prerequisite.objects.get_or_create(
               course=cs81,
               requisite=cs60,
               )
    cp.alternates = [cs42,]
    Prerequisite.objects.get_or_create(
               course=cs81,
               requisite=math55,
               )
    Prerequisite.objects.get_or_create(
               course=cs105,
               requisite=cs70,
               )
    Prerequisite.objects.get_or_create(
               course=cs121,
               requisite=cs70,
               )
    Prerequisite.objects.get_or_create(
               course=cs131,
               requisite=cs70,
               )
    Prerequisite.objects.get_or_create(
               course=cs131,
               requisite=cs81,
               )
    Prerequisite.objects.get_or_create(
               course=cs140,
               requisite=cs70,
               )
    Prerequisite.objects.get_or_create(
               course=cs140,
               requisite=math55,
               )
    requirements = [(cs60,cs42),
                    cs70,
                    cs81,
                    cs105,
                    cs121,
                    cs131,
                    cs140,
                    math55]
    cs, new = Major.objects.get_or_create(title="Computer Science")
    cs.departments.add(csci)
    create_requirements(requirements, cs, **kwargs)
    
    
    
def create_majors(sender, **kwargs):
    create_major_HM_CSCI(**kwargs)
#signals.post_syncdb.connect(create_majors, features)
    
    
