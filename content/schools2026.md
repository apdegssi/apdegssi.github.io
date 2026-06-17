---
title: "Analytic and Geometric aspects of evolutionary PDEs"
date: 2026-03-26
draft: false
aliases:
  - /school2026/
  - /school/
  - /schools/
---

Summer school on **Analytic and Geometric Aspects of Evolutionary PDEs**. The poster of the school can be found [here](/postergssi2026.pdf)

### Event Schedule

* Starts: Monday, September 14, 2026, at 9:00 AM
* Ends: Friday, September 18, 2026, at 11:30 AM 

<br>


### Registration & Financial Support

Registration for the school is mandatory, and the official registration link is available [here](https://indico.gssi.it/event/956/). 

GSSI offers limited financial support to students and early-career researchers wishing to attend. During the application for funding, you will be asked to upload a CV and a motivation letter, combined into a single document.

Additionally, you will be ask you to provide the name and contact details of a referee who can supply a letter of recommendation upon request.

#### Key Deadlines:

* Financial Support: **31 May 2026**
* Registration: **30 June 2026**

<br>
<br>


### Speakers

{{< create_school_table "school2026" >}}

 <!-- TIMETABLE:START -->
<style>
  .apde-tt{
    --tt-ink:#1f2328;
    --tt-muted:#6b7280;
    --tt-line:#e7e7ea;
    --tt-soft:#f6f6f4;
    --tt-anderson:#3a6ea5;   --tt-anderson-bg:#ebf0f6;
    --tt-elgindi:#3f8f64;   --tt-elgindi-bg:#ecf4f0;
    --tt-marconi:#c0892c;   --tt-marconi-bg:#f9f3ea;
    margin:3rem 0;
    color:var(--tt-ink);
    -webkit-font-smoothing:antialiased;
  }
  .apde-tt .tt-head{ margin-bottom:1.4rem; }
  .apde-tt h2{
    font-family:Georgia,"Iowan Old Style","Palatino Linotype",serif;
    font-size:1.9rem; font-weight:600; letter-spacing:-.015em;
    margin:0 0 .35rem; line-height:1.1;
  }
  .apde-tt .tt-sub{
    color:var(--tt-muted); margin:0; font-size:.92rem;
    display:flex; flex-wrap:wrap; gap:.5rem .9rem; align-items:center;
  }
  .apde-tt .tt-sub .dot{ width:3px; height:3px; border-radius:50%; background:#c9c9cf; }

  .apde-tt .tt-card{
    border:1px solid var(--tt-line); border-radius:14px; overflow:hidden;
    box-shadow:0 1px 2px rgba(18,20,25,.04), 0 10px 24px -18px rgba(18,20,25,.25);
    background:#fff;
  }
  .apde-tt .tt-scroll{ overflow-x:auto; -webkit-overflow-scrolling:touch; }
  .apde-tt table{
    border-collapse:separate; border-spacing:0; width:100%; min-width:720px;
    font-size:.9rem; line-height:1.35;
  }
  .apde-tt thead th{
    background:var(--tt-soft); color:var(--tt-ink); font-weight:600;
    text-align:left; padding:.8rem .85rem; white-space:nowrap;
    border-bottom:1px solid var(--tt-line);
  }
  .apde-tt thead th + th{ border-left:1px solid var(--tt-line); }
  .apde-tt thead th .tt-date{
    display:block; font-weight:400; font-size:.76rem; color:var(--tt-muted);
    margin-top:.1rem; letter-spacing:.01em;
  }
  .apde-tt tbody td{
    padding:.6rem .85rem; vertical-align:middle;
    border-bottom:1px solid var(--tt-line); border-left:1px solid var(--tt-line);
  }
  .apde-tt tbody td:first-child{ border-left:0; }
  .apde-tt tbody tr:last-child td{ border-bottom:0; }
  .apde-tt td.tt-time{
    color:var(--tt-muted); white-space:nowrap; font-variant-numeric:tabular-nums;
    font-size:.8rem; letter-spacing:.01em; width:7.5rem; background:#fcfcfb;
  }

  .apde-tt .lec{
    border-left:3px solid var(--accent); padding-left:.65rem !important;
    background:var(--bg); transition:transform .12s ease, box-shadow .12s ease;
  }
  .apde-tt .lec .tt-speaker{ display:block; font-weight:600; color:var(--tt-ink); }
  .apde-tt .lec .tt-topic{ color:var(--tt-muted); font-size:.78rem; }
  .apde-tt .lec:hover{ transform:translateY(-1px); box-shadow:inset 0 0 0 1px var(--accent); }

  .apde-tt td.has-link{ position:relative; cursor:pointer; }
  .apde-tt .tt-stretch{ position:absolute; inset:0; z-index:1; }
  .apde-tt td.tt-note.has-link:hover,
  .apde-tt td.tt-excursion.has-link:hover{ text-decoration:underline; }
  .apde-tt .c-anderson{ --accent:var(--tt-anderson); --bg:var(--tt-anderson-bg); }
  .apde-tt .c-elgindi{ --accent:var(--tt-elgindi); --bg:var(--tt-elgindi-bg); }
  .apde-tt .c-marconi{ --accent:var(--tt-marconi); --bg:var(--tt-marconi-bg); }

  .apde-tt .tt-break td{
    background:var(--tt-soft); color:var(--tt-muted);
    text-align:center; font-size:.72rem; letter-spacing:.14em;
    text-transform:uppercase; padding:.45rem;
  }
  .apde-tt td.tt-breakcell{
    background:var(--tt-soft); color:var(--tt-muted);
    text-align:center; font-size:.72rem; letter-spacing:.14em;
    text-transform:uppercase;
  }
  .apde-tt .tt-note{ color:var(--tt-muted); text-align:center; }
  .apde-tt .tt-excursion{
    text-align:center; font-weight:500; color:var(--tt-ink); background:#fbfaf7;
  }

  .apde-tt .tt-legend{ display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.1rem; }
  .apde-tt .tt-legend .chip{
    display:inline-flex; align-items:center; gap:.5rem;
    border:1px solid var(--tt-line); border-radius:999px;
    padding:.35rem .75rem .35rem .6rem; font-size:.82rem; color:var(--tt-ink);
    background:#fff;
  }
  .apde-tt .tt-legend .chip b{ font-weight:600; }
  .apde-tt .tt-legend .chip span{ color:var(--tt-muted); }
  .apde-tt .tt-legend .chip i{ width:.7rem; height:.7rem; border-radius:50%; }
  .apde-tt .tt-legend a.chip{
    text-decoration:none; color:inherit; cursor:pointer;
    transition:border-color .12s ease, box-shadow .12s ease;
  }
  .apde-tt .tt-legend a.chip:hover{
    border-color:#c7c7cc; box-shadow:0 1px 2px rgba(18,20,25,.06);
  }
  .apde-tt .tt-legend a.chip:hover b,
  .apde-tt .tt-legend a.chip:hover span{ text-decoration:underline; }

  @media (max-width:560px){
    .apde-tt h2{ font-size:1.55rem; }
    .apde-tt .tt-legend .chip span{ display:none; }
  }
  @media (prefers-reduced-motion:reduce){ .apde-tt .lec{ transition:none; } }
  @media print{
    .apde-tt .tt-card{ box-shadow:none; }
    .apde-tt .tt-scroll{ overflow:visible; }
    .apde-tt table{ min-width:0; }
  }
</style>

<section class="apde-tt" id="timetable">
  <div class="tt-head">
    <h2>Timetable</h2>
  </div>

  <div class="tt-card">
    <div class="tt-scroll">
      <table>
        <thead>
        <tr>
          <th class="tt-time">Time</th>
          <th>Monday<span class="tt-date">14 Sep</span></th>
          <th>Tuesday<span class="tt-date">15 Sep</span></th>
          <th>Wednesday<span class="tt-date">16 Sep</span></th>
          <th>Thursday<span class="tt-date">17 Sep</span></th>
          <th>Friday<span class="tt-date">18 Sep</span></th>
        </tr>
        </thead>
        <tbody>
          <tr><td class="tt-time">09:00 &ndash; 10:00</td><td class="lec c-anderson has-link"><span class="tt-speaker">Anderson</span><span class="tt-topic">Lecture 1</span><a class="tt-stretch" href="/courses/anderson/" aria-label="Anderson — Lecture 1"></a></td><td class="lec c-marconi has-link"><span class="tt-speaker">Marconi</span><span class="tt-topic">Lecture 2</span><a class="tt-stretch" href="/courses/marconi/" aria-label="Marconi — Lecture 2"></a></td><td class="lec c-elgindi has-link"><span class="tt-speaker">Elgindi</span><span class="tt-topic">Lecture 3</span><a class="tt-stretch" href="/courses/elgindi/" aria-label="Elgindi — Lecture 3"></a></td><td class="lec c-anderson has-link"><span class="tt-speaker">Anderson</span><span class="tt-topic">Lecture 4</span><a class="tt-stretch" href="/courses/anderson/" aria-label="Anderson — Lecture 4"></a></td><td class="tt-note">Open problems</td></tr>
          <tr class="tt-break"><td class="tt-time">10:00 &ndash; 10:30</td><td colspan="5">Coffee</td></tr>
          <tr><td class="tt-time">10:30 &ndash; 11:30</td><td class="lec c-elgindi has-link"><span class="tt-speaker">Elgindi</span><span class="tt-topic">Lecture 1</span><a class="tt-stretch" href="/courses/elgindi/" aria-label="Elgindi — Lecture 1"></a></td><td class="lec c-anderson has-link"><span class="tt-speaker">Anderson</span><span class="tt-topic">Lecture 2</span><a class="tt-stretch" href="/courses/anderson/" aria-label="Anderson — Lecture 2"></a></td><td class="lec c-marconi has-link"><span class="tt-speaker">Marconi</span><span class="tt-topic">Lecture 3</span><a class="tt-stretch" href="/courses/marconi/" aria-label="Marconi — Lecture 3"></a></td><td class="lec c-elgindi has-link"><span class="tt-speaker">Elgindi</span><span class="tt-topic">Lecture 4</span><a class="tt-stretch" href="/courses/elgindi/" aria-label="Elgindi — Lecture 4"></a></td><td class="tt-note">Closing and discussion<br><small>(ends 11:30)</small></td></tr>
          <tr><td class="tt-time">11:45 &ndash; 12:45</td><td class="lec c-marconi has-link"><span class="tt-speaker">Marconi</span><span class="tt-topic">Lecture 1</span><a class="tt-stretch" href="/courses/marconi/" aria-label="Marconi — Lecture 1"></a></td><td class="lec c-elgindi has-link"><span class="tt-speaker">Elgindi</span><span class="tt-topic">Lecture 2</span><a class="tt-stretch" href="/courses/elgindi/" aria-label="Elgindi — Lecture 2"></a></td><td class="lec c-anderson has-link"><span class="tt-speaker">Anderson</span><span class="tt-topic">Lecture 3</span><a class="tt-stretch" href="/courses/anderson/" aria-label="Anderson — Lecture 3"></a></td><td class="lec c-marconi has-link"><span class="tt-speaker">Marconi</span><span class="tt-topic">Lecture 4</span><a class="tt-stretch" href="/courses/marconi/" aria-label="Marconi — Lecture 4"></a></td><td class="tt-note">&mdash;</td></tr>
          <tr class="tt-break"><td class="tt-time">12:45 &ndash; 14:30</td><td colspan="5">Lunch</td></tr>
          <tr><td class="tt-time">from 14:30</td><td class="tt-note">Contributed talks</td><td class="tt-note">Discussions</td><td class="tt-excursion">Social excursion</td><td class="tt-note">Contributed talks</td><td class="tt-note">&mdash;</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="tt-legend">
    <a class="chip" href="/courses/anderson/"><i style="background:var(--tt-anderson)"></i><b>Anderson</b>&nbsp;<span>Stability and instability in nonlinear hyperbolic PDEs</span></a>
    <a class="chip" href="/courses/elgindi/"><i style="background:var(--tt-elgindi)"></i><b>Elgindi</b>&nbsp;<span>Coherent structures in incompressible fluids</span></a>
    <a class="chip" href="/courses/marconi/"><i style="background:var(--tt-marconi)"></i><b>Marconi</b>&nbsp;<span>Entropy solutions to scalar conservation laws</span></a>
  </div>
</section>
<!-- TIMETABLE:END -->

