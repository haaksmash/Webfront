'''
Created on May 2, 2012

@author: Haak Saxberg
'''
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from ...models import Campus, Semester, Day, Course, Prerequisite

from itertools import izip
import csv, pprint, re, datetime

class Command(BaseCommand):
    args = '<directory_of_csv_files>'
    help = 'Populates the Course tables with information from csv files.'
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Expects a single directory as an argument.")
        dir = args[0]
        if dir[-1] != '/':
            
            dir += '/'
        
        # Gather up the relevant csv files.
        # ENSURE THESE ARE ENCODED AS UTF-8 BEFORE RUNNING THIS SCRIPT
        PREREQS = open(dir + 'courses 3.csv')
        
        # Gather campuses. We'll need them later.
        CAMPUS_CODES = Campus.objects.all().values_list('code', flat=True)
        self.stderr.write("{}".format(CAMPUS_CODES))
        CAMPUS_LOOKUP = dict([ x for x in izip(CAMPUS_CODES,
                                               Campus.objects.all())])
        def find_campus(string, dictionary):
            try:
                camp = CAMPUS_LOOKUP[string]
            except KeyError, e:
                print "Invalid campus: {}".format(string)
                try:
                    camp = CAMPUS_LOOKUP[dictionary['campus']]
                except KeyError, e:
                    print "Falling back to NA"
                    camp = CAMPUS_LOOKUP['NA']
            return camp
        
        SEMESTER_LOOKUP = dict([ x for x in izip(Semester.objects.values_list('half','year'),
                                                 Semester.objects.all())])
        
        DAY_LOOKUP = dict([x for x in izip(Day.objects.values_list('code',flat=True),
                                           Day.objects.all())])
        
        self.stderr.write("{}\n{}\n{}".format(CAMPUS_LOOKUP, SEMESTER_LOOKUP, DAY_LOOKUP))
        
        prereqs_r = csv.DictReader(PREREQS)
        
        for row in prereqs_r:
            # C = Corequisite, P = Prerequisite, N = Concurrent Enrollment Required
            if row['Requisite Course Category'] in ['C', 'N', 'P']:
                
                code = row['\xef\xbb\xbf"Course Number"'] # ugly because of utf-8 force encoding
                #self.stderr.write("Parsing requisites for {}\n".format(code))
                try:
                    c = Course.objects.get(codeletters=code[:4],
                                            codenumber=code[4:9],
                                            codecampus=code[9:])
                except ObjectDoesNotExist:
                    print "Non-existent course with requisites: {}".format(code)
                    continue
                print "Found course with requisites: ",c.code
                
                req_cat = row['Requisite Course Category']
                # get rid of '*' runs; they only happen at the end or at the
                # beginning, as far as I can tell.
                req_code = re.sub(r'\*+', '*', row['Requisite Course Number'])
                filter = {
                          'starts':"{}__istartswith",
                          'ends':"{}__iendswith",
                          'is':"{}",
                         }
                req_els = req_code.split('*')
                if len(req_els) == 1:
                    # a non-wildcard requirement
                    try:
                        r = Course.objects.get(code=req_els[0])
                    except ObjectDoesNotExist, e:
                        print "\tNo such course: {}".format(req_els[0])
                        continue
                
                    
                    if req_cat == 'N':
                        c.concurrent_with.add(r)
                    elif req_cat == 'C':
                        c.corequisites.add(r)
                    elif req_cat == 'P':
                        p, new = Prerequisite.objects.get_or_create(
                                                        course=c,
                                                        requisite=r)
                elif len(req_els) == 2: # a single wildcard
                    if req_els[0] == '':
                        r = Course.objects.filter(**{filter['ends'].format('code'):req_els[1]})
                    else:
                        r = Course.objects.filter(**{filter['starts'].format('code'):req_els[0]})
                    
                    
                    if req_cat == 'N':
                        c.concurrent_with.add(*r)    
                    elif req_cat == 'C':
                        c.corequisites.add(*r)
                    elif req_cat == 'P':
                        p = None
                        for alt in r:
                            if p == None:
                                p, new = Prerequisite.objects.get_or_create(
                                                        course=c,
                                                        requisite=alt
                                                                            )
                                continue
                            p.alternates.add(alt)
                            
                elif len(req_els) >= 3: # this is stupid.
                    print "\tFuck this prereq: {}".format(c.code)