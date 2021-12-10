/** Get the resume header/personal details */
SELECT resume.*, obj.objective
FROM objective obj
JOIN  resume ON obj.resume_id = resume.id
WHERE resume.id = 1;

/** Get the set of skills */
SELECT resume.id, skills.type, skills.name
FROM skill skl
JOIN resume ON skl.resume_id = resume.id
WHERE resume.id = ?;

/** Get the set of schools/education */
SELECT resume.id, edu.school, edu.location, edu.start_year, edu.end_year, 
                edu.program
FROM education edu
JOIN resume ON edu.resume_id = resume.id
WHERE resume.id = ?;

/** Get the set of companies/experience */
SELECT resume.id, exp.id, exp.company_name, exp.location,
                exp.start_year, exp.end_year, exp.title
FROM experience exp
JOIN resume ON exp.resume_id = resume.id 
WHERE resume.id  = ?;

/** For Each company get the set of accomplishments */
SELECT exp.id, acc.text
FROM accomplishment acc
JOIN experience exp ON acc.company_id = exp.id
WHERE exp.id  = ? AND exp.resume_id = ?;
