## Model details

What's being modelled is a set of lecturers and a set of students, where the lecturers allocate coursework and a limited amount of extracurricular work, and students accept these responsibilities and discharge them appropriately.

A student should be given a set of coursework of fairly high importance, requiring resources such as time and either essays produced or code written. Lecturers should then give out time-sensitive responsibilities, either writing research code or producing a paper.

Comparisons are made between models where these agents are "responsible", and agents where no responsibility formalism is introduced. Extra-curricular work should be performed better when modelled in the responsible setting.

---

## Things that happen in this model

Every 30 ticks, students are given coursework by lecturers. Some students are responsible, others not so.

Every 70 ticks, lecturers pick one student from their class to assign extracurricular work. Students can accept that work, or decline it. If it's declined, lecturers pass the work on to their next choice. Eventually, one student will presumably accept the work.

Run this for a long time and see what happens. 
