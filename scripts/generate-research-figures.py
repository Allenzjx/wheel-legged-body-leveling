"""Regenerate archived scientific figures from their retained derived CSV.

Requires Python, pandas, numpy and matplotlib. Optional --source-root rebuilds
the derived CSV from the original, read-only project evidence directory.
"""
from pathlib import Path
import argparse, csv, hashlib, json, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source-root', type=Path, help='Original robotics project root; read only')
args = parser.parse_args()
ARCHIVE = ROOT / 'research' / 'archive' / '2026-10-31'
DATA = ARCHIVE / 'data'; FIG = ARCHIVE / 'figures'
DATA.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
METRICS = ['exact_body_tilt_rms_deg', 'peak_body_tilt_deg', 'roll_rms_deg', 'pitch_rms_deg']
METHODS = ['recording', 'updated_ppo']
LABELS = {'recording':'Recorded Replay', 'updated_ppo':'Residual PPO'}
COLORS = {'recording':'#7C7484', 'updated_ppo':'#164889'}

if args.source_root:
    base = args.source_root / 'ppo_reliability_20261030_14h'
    source_files = {
        'regression_csv': base/'analysis100/final_regression39/all39_compact_comparison.csv',
        'regression_report': base/'analysis100/final_regression39/comparison.json',
        'holdout_csv': base/'analysis100/final_holdout8/all_holdout_conditions.csv',
        'holdout_report': base/'analysis100/final_holdout8/holdout8_comparison.json',
        'nominal_report': base/'poster_update_100mm/analysis/nominal_head04_evidence.json',
    }
    reg = pd.read_csv(source_files['regression_csv'])
    hold = pd.read_csv(source_files['holdout_csv'])
    rows = []
    for _, row in reg.iterrows():
        for method in METHODS:
            item = {'cohort':'known_regression_39', 'case_id':row['case_id'], 'height_mm':100,
                    'target_gap_mm':row['target_gap_mm'], 'friction_scale':row['friction_scale'],
                    'method':method}
            for rule in ['common_success','native_success','both_success']:
                item[rule] = bool(row[f'{method}_{rule}'])
            for metric in METRICS:
                item[f'geometric_prefix_{metric}'] = row[f'{method}_geometric_prefix_{metric}']
                item[f'full_episode_{metric}'] = row[f'{method}_{metric}']
            item['full_episode_duration_s'] = row[f'{method}_duration_s']
            item['native_failure_reason'] = row[f'{method}_native_failure_reason']
            rows.append(item)
    for _, row in hold[hold.role.isin(METHODS)].iterrows():
        item = {'cohort':'predeclared_holdout_8','case_id':row['case_id'],'height_mm':100,
                'target_gap_mm':row['target_gap_mm'],'friction_scale':row['friction_scale'],
                'method':row['role']}
        for rule in ['common_success','native_success','both_success']:
            item[rule] = bool(row[rule])
        for metric in METRICS:
            item[f'geometric_prefix_{metric}'] = row[f'geometric_prefix_{metric}']
            item[f'full_episode_{metric}'] = row[f'full_episode_{metric}']
        item['full_episode_duration_s'] = row['full_episode_duration_s']
        item['native_failure_reason'] = row['native_failure_reason']
        rows.append(item)
    frame = pd.DataFrame(rows)
    frame.to_csv(DATA/'evaluation-100mm.csv',index=False,encoding='utf-8',float_format='%.15g')
    reports = {key:json.loads(source_files[key].read_text()) for key in ['regression_report','holdout_report']}
    expected_counts = {name:reports[key]['success_counts'] for name,key in [('known_regression_39','regression_report'),('predeclared_holdout_8','holdout_report')]}
    for cohort, subset in frame.groupby('cohort'):
        for method, group in subset.groupby('method'):
            for col, key in [('common_success','common'),('native_success','native'),('both_success','both')]:
                assert int(group[col].sum()) == expected_counts[cohort][method][key], (cohort,method,col)
    provenance = {
        'schema':'robot-project-site.research-data.v2',
        'height_mm':100,
        'model':'Updated 100 mm controller: frozen joint policy plus learned two-gain wheel head, head_04',
        'checkpoint_sha256':reports['regression_report']['checkpoint_sha256'],
        'cohorts':{'known_regression_39':'39 known development/regression conditions; not unseen generalization',
                   'predeclared_holdout_8':'8 predeclared conditions evaluated after checkpoint selection was frozen'},
        'methods':LABELS,
        'source_files':[{'name':str(p.relative_to(base)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in source_files.values()],
        'measurement':'Measured simulation state; posture metrics use native 120 Hz samples.',
        'metric_windows':{
            'geometric_prefix':'Start through each method\'s geometric completion. Failed episodes may not complete; main posture plots include only pairs where both methods strictly succeed.',
            'full_episode':'Entire method-specific episode, retained separately in the CSV. Do not substitute this window for geometric-prefix figures.'},
        'definitions':{
            'exact_body_tilt_rms_deg':'Time RMS of total body inclination alpha = acos(cos(roll) * cos(pitch)), in degrees.',
            'both_success':'Intersection of common completion and native success (strict success).',
            'paired_percent_change':'100 * (Residual PPO value / Recorded Replay value - 1); mean is the mean of per-case percentage changes.',
            'target_gap_mm':'Configured initial gap target, not a claim that every post-startup measured gap is identical.'},
        'limits':['One frozen controller, selected conditions and simulation only.','No confidence intervals or statistical significance claim are inferred from these deterministic case suites.','Lower tilt RMS does not imply lower peak, pitch RMS or all support metrics.','Complete-controller comparisons do not isolate PPO as the sole cause.']
    }
    (DATA/'evaluation-100mm-provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    for suffix in ['png','svg']:
        shutil.copyfile(base/f'poster_update_100mm/media/phase_roll_pitch_head04.{suffix}', FIG/f'nominal-100mm-roll-pitch.{suffix}')
    nominal=json.loads(source_files['nominal_report'].read_text())
    phase_rows=[]
    for chart in nominal['bar_charts']:
        for series in chart['series']:
            for phase,value in zip(chart['categories'],series['values']):
                phase_rows.append({'phase':phase,'method':series['method'],'metric':chart['metric'],'value_deg':value})
    pd.DataFrame(phase_rows).to_csv(DATA/'nominal-100mm-phase-metrics.csv',index=False,float_format='%.15g')
    phase_note={
        'case_id':nominal['case_id'],'height_mm':100,'sample_hz':120,
        'window_source':'Recorded Replay; unchanged windows applied to both methods',
        'boundary':'start_tick_exclusive < tick <= end_tick_inclusive',
        'windows':{k:{'start_tick_exclusive':v['start_tick_exclusive'],'end_tick_inclusive':v['end_tick_inclusive'],
                      'start_s':v['start_tick_exclusive']/120,'end_s':v['end_tick_inclusive']/120}
                   for k,v in nominal['phase_contract']['phases'].items()},
        'rms_definition':nominal['phase_metric_definition'],'FR_pooling':nominal['FR_aggregation'],
        'sampling':nominal['sampling_separation'],
        'source_report_sha256':hashlib.sha256(source_files['nominal_report'].read_bytes()).hexdigest()}
    (DATA/'nominal-100mm-phase-windows.json').write_text(json.dumps(phase_note,indent=2),encoding='utf-8')

frame = pd.read_csv(DATA/'evaluation-100mm.csv')
assert len(frame)==94 and frame.groupby('cohort').case_id.nunique().to_dict()=={'known_regression_39':39,'predeclared_holdout_8':8}
for column in ['common_success','native_success','both_success']:
    if frame[column].dtype != bool:
        frame[column] = frame[column].astype(str).str.lower().eq('true')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.titleweight':'semibold',
    'axes.labelsize':10,'axes.edgecolor':'#657180','axes.labelcolor':'#263343','text.color':'#263343',
    'xtick.color':'#4E5968','ytick.color':'#4E5968','axes.spines.top':False,'axes.spines.right':False,
    'grid.color':'#DCE1E7','grid.linewidth':.7,'svg.fonttype':'none','savefig.facecolor':'white'})
def save(fig,stem):
    fig.savefig(FIG/f'{stem}.png',dpi=200,bbox_inches='tight',pad_inches=.16)
    fig.savefig(FIG/f'{stem}.svg',bbox_inches='tight',pad_inches=.16)
    plt.close(fig)
def paired(cohort):
    sub=frame[frame.cohort.eq(cohort)]
    r=sub[sub.method.eq('recording')].set_index('case_id'); p=sub[sub.method.eq('updated_ppo')].set_index('case_id')
    ids=r.index[r.both_success&p.both_success]
    return r.loc[ids],p.loc[ids]

fig,axes=plt.subplots(1,2,figsize=(10,4.7),layout='constrained')
means={}
for ax,cohort,title,expected in zip(axes,['known_regression_39','predeclared_holdout_8'],['A  Known regression conditions','B  Predeclared held-out conditions'],[25,5]):
    r,p=paired(cohort); assert len(r)==expected
    col='geometric_prefix_exact_body_tilt_rms_deg'; change=(1-p[col]/r[col])*100;means[cohort]=float(change.mean())
    ax.plot([10,17],[10,17],color='#818B98',lw=1,ls='--',label='Equal tilt RMS')
    ax.scatter(r[col],p[col],s=43,color=COLORS['updated_ppo'],alpha=.83,edgecolors='white',linewidths=.55,label='Matched condition',zorder=3)
    ax.set(xlim=(10,17),ylim=(10,17),xlabel='Recorded Replay tilt RMS (°)',ylabel='Residual PPO tilt RMS (°)')
    ax.set_aspect('equal');ax.grid(alpha=.7);ax.set_axisbelow(True);ax.set_title(title,loc='left',pad=13)
    ax.text(.04,.95,f'{len(r)} jointly strict-successful pairs\nMean paired reduction: {change.mean():.1f}%',transform=ax.transAxes,va='top',fontsize=9.2)
    ax.text(.96,.08,'Below diagonal = lower PPO tilt RMS',transform=ax.transAxes,ha='right',fontsize=8.4,color=COLORS['updated_ppo'])
axes[0].legend(loc='upper left',bbox_to_anchor=(.02,.80),frameon=False,fontsize=8.5)
save(fig,'100mm-paired-tilt-scatter')
assert abs(means['known_regression_39']-16.6999119466)<1e-8
assert abs(means['predeclared_holdout_8']-14.495855897778942)<1e-8

fig,ax=plt.subplots(figsize=(9,4.4),layout='constrained')
r,p=paired('predeclared_holdout_8')
labels=['Total-tilt RMS','Peak total tilt','Roll RMS','Pitch RMS']; tradeoffs={}
for y,(metric,label) in enumerate(zip(METRICS,labels)):
    col='geometric_prefix_'+metric;values=100*(p[col]/r[col]-1);tradeoffs[metric]=float(values.mean())
    ax.scatter(values,np.full(5,y)+np.linspace(-.11,.11,5),s=47,color=COLORS['updated_ppo'],edgecolors='white',lw=.6,zorder=3,label='Individual paired condition' if y==0 else None)
    ax.scatter([values.mean()],[y+.24],s=54,marker='D',color='#263343',zorder=4,label='Mean of paired changes' if y==0 else None)
    ax.text(36,y,f'{values.mean():+.1f}%',va='center',fontsize=10)
ax.axvline(0,color='#5B6674',lw=1.1)
ax.set(xlim=(-35,44),ylim=(3.6,-.6),yticks=range(4),yticklabels=labels,xlabel='Change relative to Recorded Replay (%)')
ax.set_xticks([-30,-20,-10,0,10,20,30]);ax.xaxis.set_major_formatter(lambda x,pos:f'{x:+.0f}' if x else '0')
ax.grid(axis='x',alpha=.7);ax.set_axisbelow(True);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0,pad=12)
ax.set_title('Held-out posture tradeoffs · five jointly strict-successful pairs',loc='left',pad=23)
ax.text(36,-.44,'Mean',fontsize=9,color='#4E5968')
ax.legend(loc='upper left',bbox_to_anchor=(0,-.22),ncol=2,frameon=False,fontsize=9)
save(fig,'100mm-holdout-tradeoffs')

fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
for ax,cohort,title,n in zip(axes,['known_regression_39','predeclared_holdout_8'],['A  Known regression conditions (n = 39)','B  Predeclared held-out conditions (n = 8)'],[39,8]):
    sub=frame[frame.cohort.eq(cohort)];x=np.arange(2);width=.31
    for offset,method in zip([-.5,.5],METHODS):
        selected=sub[sub.method.eq(method)];counts=[int(selected.common_success.sum()),int(selected.both_success.sum())]
        bars=ax.bar(x+offset*width,np.array(counts)/n*100,width=width,color=COLORS[method],label=LABELS[method],zorder=3)
        for bar,count in zip(bars,counts):ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+2,f'{count}/{n}',ha='center',va='bottom',fontsize=10,fontweight='semibold')
    ax.set(xticks=x,xticklabels=['Common completion','Strict success'],ylim=(0,113),ylabel='Conditions completed (%)')
    ax.set_yticks([0,25,50,75,100]);ax.yaxis.set_major_formatter(PercentFormatter(100));ax.grid(axis='y');ax.set_axisbelow(True);ax.set_title(title,loc='left',pad=14)
axes[0].legend(loc='upper center',bbox_to_anchor=(1.09,-.14),ncol=2,frameon=False)
save(fig,'100mm-completion-counts')

fig,ax=plt.subplots(figsize=(8.6,4.8),layout='constrained')
for cohort,label,color,marker in [('known_regression_39','Known regression · 39 conditions',COLORS['recording'],'o'),('predeclared_holdout_8','Predeclared held-out · 8 conditions',COLORS['updated_ppo'],'^')]:
    sub=frame[frame.cohort.eq(cohort)&frame.method.eq('recording')]
    ax.scatter(sub.target_gap_mm,sub.friction_scale,s=50 if marker=='o' else 66,color=color,marker=marker,edgecolors='white',lw=.7,alpha=.9,label=label,zorder=3)
ax.set(xlabel='Initial gap target (mm)',ylabel='Friction scale',xlim=(193,244),ylim=(.43,1.57))
ax.set_title('Evaluation conditions · 100 mm step height',loc='left',pad=15);ax.grid();ax.set_axisbelow(True)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.17),ncol=2,frameon=False,fontsize=9)
save(fig,'100mm-evaluation-conditions')

summary={'paired_geometric_tilt_rms_reduction_percent':means,'holdout_mean_paired_change_percent':tradeoffs,
         'n_rows':len(frame),'cohort_conditions':{'known_regression_39':39,'predeclared_holdout_8':8},
         'plot_pairs':{'known_regression_39':25,'predeclared_holdout_8':5}}
(DATA/'figure-statistics.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
