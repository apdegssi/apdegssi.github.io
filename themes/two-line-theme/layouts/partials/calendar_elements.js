var events = [
    {
        daysOfWeek: [0, 6],
        rendering: "background",
        color: "#eee",
        overLap: false,
        allDay: true
    },
{{ range where  (sort .Site.Pages "LinkTitle") ".Params.tags" "in" "course" }}
    { start: "{{ .Params.begin }} 2025", title: "Course by {{ .Params.author }}" 
      end: "{{ .Params.end }} 2025"
     },
{{ end }}
    // { start: "2020-06-02", title: "2h, 1 issue", classNames: "warning" },
    // { start: "2020-06-03", title: "8h 0m, 1 issue" },
    // { start: "2020-06-04", title: "8h 15m, 2 issues" },
    // { start: "2020-06-05", title: "8h, 1 issue" },
    // //start: '2020-06-06', title: '8h' },
    // //start: '2020-06-07', title: '8h' },
    // { start: "2020-06-08", title: "8h, 2 issues" },
    // { start: "2020-06-09", title: "8h, 4 issues" },
    // { start: "2020-06-10", title: "8h, 1 issue" },
    // { start: "2020-06-11", title: "0h", classNames: "error" },
    // // Multiple event on one day example
    // { start: "2020-06-15", title: "2h", issueKey: "TAS-123" },
    // { start: "2020-06-15", title: "2h", issueKey: "TT-456" },
    // { start: "2020-06-15", title: "2h", issueKey: "IDT-123" },
    // { start: "2020-06-15", title: "2h", issueKey: "IDT-124" }
    // Future events not displayed...
    // { start: '2020-06-12', title: '8h' },
    // //start: '2020-06-13', title: '8h' },
    // //start: '2020-06-14', title: '8h' },
    // { start: '2020-06-15', title: '8h' },
    // { start: '2020-06-16', title: '8h' },
    // { start: '2020-06-17', title: '8h' },
    // { start: '2020-06-18', title: '8h' },
    // { start: '2020-06-19', title: '8h' },
    // //start: '2020-06-20', title: '8h' },
    // //start: '2020-06-21', title: '8h' },
    // { start: '2020-06-22', title: '8h' },
    // { start: '2020-06-23', title: '8h' },
    // { start: '2020-06-24', title: '8h' },
    // { start: '2020-06-25', title: '8h' },
    // { start: '2020-06-26', title: '8h' },
    // //start: '2020-06-27', title: '8h' },
    // //start: '2020-06-28', title: '8h' },
    // { start: '2020-06-29', title: '8h' },
    // { start: '2020-06-30', title: '8h' },
];
