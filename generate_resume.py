from contextlib import closing
import argparse
import os
import sqlite3

from jinja2 import Environment, FileSystemLoader


def build_resume_details():

    # Resume data to pass to Jinja templates
    resume = {}

    # Get connection to sqlite3 database
    with closing(sqlite3.connect("resume.sqlite")) as conn:
        conn.row_factory = sqlite3.Row

        # Get the Resume details
        with closing(conn.cursor()) as resume_cur:
            row = resume_cur.execute("""
                SELECT resume.*, obj.objective
                FROM objective obj
                JOIN  resume ON obj.resume_id = resume.id
                WHERE resume.id = 1;
            """).fetchone()

            for data in row.keys():
                resume[data] = row[data]

        # Get the Resume Skills section and populate the template details
        with closing(conn.cursor()) as skills_cur:
            rows = skills_cur.execute("""
                SELECT skl.type, skl.name
                FROM skills skl
                JOIN resume ON skl.resume_id = resume.id
                WHERE resume.id = ?;
            """, str(resume["id"])).fetchall()

            resume["skills"] = {}
            for row in rows:
                # If adding a new skill type then create and empty list
                if row["type"] not in resume["skills"]:
                    resume["skills"][row["type"]] = []

                resume["skills"][row["type"]].append(row["name"])

        # Get the Resume Education section and populate the template details
        with closing(conn.cursor()) as edu_cur:
            rows = edu_cur.execute("""
                SELECT edu.school, edu.location, edu.program,
                    edu.start_year, edu.end_year
                FROM education edu
                JOIN resume ON edu.resume_id = resume.id
                WHERE resume.id = ?
            """, str(resume["id"])).fetchall()

            resume["education"] = []
            for row in rows:
                institution = {}
                for key in row.keys():
                    institution[key] = row[key]
                resume["education"].append(institution.copy())

        # Get the Resume Experience section and populate the template details
        with closing(conn.cursor()) as exp_cur:
            rows = exp_cur.execute("""
                SELECT exp.id, exp.company_name, exp.location,
                                exp.title, exp.start_year, exp.end_year
                FROM experience exp
                JOIN resume ON exp.resume_id = resume.id
                WHERE resume.id  = ?;
            """, str(resume["id"])).fetchall()

            resume["experience"] = []
            for row in rows:
                company = {}
                for key in row.keys():
                    company[key] = row[key]

                # Get the Resume Accomplishment section and populate the
                # template details
                company['accomplishments'] = []
                with closing(conn.cursor()) as acc_cur:
                    rows = acc_cur.execute("""
                        SELECT exp.id, acc.text
                            FROM accomplishment acc
                            JOIN experience exp ON acc.company_id = exp.id
                            WHERE exp.id  = ? AND exp.resume_id = ?;
                    """, [str(company["id"]), str(resume["id"])]).fetchall()
                    for row in rows:
                        accomplish = {}
                        for key in row.keys():
                            accomplish[key] = row[key]
                        company['accomplishments'].append(accomplish.copy())

                # Add complete experience/accomplishment record to resume
                resume["experience"].append(company.copy())

    return resume


def main(template, output):

    # Setup Jinja2 template loading
    template_loader = FileSystemLoader(searchpath=template)
    env = Environment(loader=template_loader)

    # render the Resume
    resume = build_resume_details()
    tmpl = env.get_template("resume.jinja")
    resume_details = tmpl.render(resume=resume)

    # Write out the resume to file if provided else
    # print it to stdout
    if (output is not None and output != ''):
        with (open(output, "w")) as resume_file:
            resume_file.write(resume_details)
    else:
        print(resume_details)


if __name__ == '__main__':
    # Parse command line
    parser = argparse.ArgumentParser(description='Generate Resume')
    parser.add_argument('--template', type=str, required=True,
                        help='Name of the resume template to use')
    parser.add_argument('--output', type=str, nargs='?', default='',
                        help='Path to output the rendered resume html file')
    args = parser.parse_args()

    # Get the directory of the resume template by name
    template_dir = f"templates/{args.template}"
    template = os.path.normpath(os.path.join(os.getcwd(), template_dir))

    main(template, args.output)
