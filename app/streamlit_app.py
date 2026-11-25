import hashlib, json, os, uuid
from pathlib import Path
import httpx
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import streamlit as st
from app.ui import chart_colors, chart_theme, empty_state, inject_theme, render_hero, render_table, section_heading
from src.preprocessing.feature_schema import MODES
from src.data.ingestion import load_dataset

load_dotenv(os.getenv("PIVOT_ENV_FILE",".env"),override=False)
if not os.getenv("MONGODB_URI") and Path("atlas-credentials.env").exists(): load_dotenv("atlas-credentials.env",override=False)

st.set_page_config(page_title="PIVOT | Student Intelligence",page_icon="◈",layout="wide")
if "pivot_theme" not in st.session_state: st.session_state["pivot_theme"]="light"
if "pivot-dark-mode" not in st.session_state: st.session_state["pivot-dark-mode"]=st.session_state["pivot_theme"]=="dark"
def sync_theme(): st.session_state["pivot_theme"]="dark" if st.session_state["pivot-dark-mode"] else "light"
inject_theme(st.session_state["pivot_theme"])
def navigate_to(destination):
    st.session_state["workspace-page"]=destination

with st.sidebar:
    st.markdown('<div class="pivot-brand"><span class="pivot-brand-mark">P</span><strong>PIVOT</strong></div>',unsafe_allow_html=True)
    st.caption("STUDENT PERFORMANCE INTELLIGENCE")
    st.toggle("Dark mode",key="pivot-dark-mode",on_change=sync_theme)
    page=st.session_state.get("workspace-page","Overview")
    st.markdown("**WORKSPACE**")
    st.button("◈  Overview",key="nav-overview",use_container_width=True,type="primary" if page=="Overview" else "secondary",on_click=navigate_to,args=("Overview",))
    st.markdown("**PROFILES**")
    for destination,label in (("Student","◉  Student profile"),("Educator","▣  Educator workspace")):
        st.button(label,key=f"nav-{destination.lower()}",use_container_width=True,type="primary" if page==destination else "secondary",on_click=navigate_to,args=(destination,))
    st.markdown("**PREDICTION TOOLS**")
    for destination,label in (("Student Prediction","⌁  Student prediction"),("What-if Simulator","↻  What-if simulator"),("Batch Analytics","⇧  Batch predictions")):
        st.button(label,key=f"nav-{destination.lower().replace(' ','-')}",use_container_width=True,type="primary" if page==destination else "secondary",on_click=navigate_to,args=(destination,))
    st.markdown("**RESEARCH**")
    st.button("Research Lab",key="nav-research",use_container_width=True,type="primary" if page=="Research Lab" else "secondary",on_click=navigate_to,args=("Research Lab",))
    st.divider(); st.caption("Research prototype · UCI Student Performance")

API=os.getenv("PIVOT_API_URL","http://127.0.0.1:8000")
FEATURE_LABELS={"school":"School","sex":"Sex","age":"Age","address":"Home address type","famsize":"Family size","Pstatus":"Parents' cohabitation","Medu":"Mother's education","Fedu":"Father's education","Mjob":"Mother's job","Fjob":"Father's job","reason":"School choice reason","guardian":"Primary guardian","traveltime":"Travel time to school","studytime":"Weekly study time","failures":"Past class failures","schoolsup":"School support","famsup":"Family support","paid":"Paid classes","activities":"Extracurricular activities","nursery":"Attended nursery school","higher":"Plans for higher education","internet":"Internet access at home","romantic":"In a romantic relationship","famrel":"Family relationship quality","freetime":"Free time after school","goout":"Going out with friends","Dalc":"Weekday alcohol use","Walc":"Weekend alcohol use","health":"Current health","absences":"School absences","G1":"Period 1 grade (G1)","G2":"Period 2 grade (G2)"}
INPUT_RANGES={"age":(15,22),"Medu":(0,4),"Fedu":(0,4),"traveltime":(1,4),"studytime":(1,4),"failures":(0,4),"famrel":(1,5),"freetime":(1,5),"goout":(1,5),"Dalc":(1,5),"Walc":(1,5),"health":(1,5),"absences":(0,93),"G1":(0,20),"G2":(0,20)}
def call_api(path,payload=None,quiet=False):
    try:
        r=httpx.post(API+path,json=payload,timeout=20) if payload is not None else httpx.get(API+path,timeout=10)
        r.raise_for_status(); return r.json()
    except httpx.HTTPStatusError as e:
        if not quiet:
            try: detail=e.response.json().get("detail","")
            except ValueError: detail=""
            if e.response.status_code==503: st.warning("A required service is unavailable. Student records may need a working MongoDB Atlas connection.")
            else: st.error(f"API request failed ({e.response.status_code}). {detail}")
        return None
    except httpx.RequestError:
        if not quiet: st.error("Cannot reach the PIVOT API. Confirm its PowerShell window is running at http://127.0.0.1:8000.")
        return None
def intro(kicker,title,desc):
    render_hero(kicker,title,desc,compact=page!="Overview")
def load_results():
    p=Path("reports/experiments/training_results.json")
    return json.loads(p.read_text()) if p.exists() else {}
def get_cohort():
    try:return load_dataset()
    except Exception:return pd.DataFrame()
def input_form(mode,key="predict"):
    cols=MODES[mode]; sample=get_cohort(); row=sample.iloc[0] if len(sample) else None
    with st.form(key):
        values={}
        academic=[c for c in ("G1","G2","studytime","failures","schoolsup","paid","higher") if c in cols]
        wellbeing=[c for c in ("famsup","activities","romantic","famrel","freetime","goout","Dalc","Walc","health","absences") if c in cols]
        context=[c for c in cols if c not in academic+wellbeing]
        sections=[("Student and family",context,"Personal, family, and school background."),("Learning and support",academic,"Grades, study habits, and academic support."),("Wellbeing and routine",wellbeing,"Daily routine, relationships, and wellbeing.")]
        tabs=st.tabs([name for name,_,_ in sections])
        for tab,(_,fields,description) in zip(tabs,sections):
            with tab:
                st.caption(description)
                if fields is context:
                    groups=[("Personal information",[c for c in fields if c in ("school","sex","age","address")]),
                            ("Family background",[c for c in fields if c in ("famsize","Pstatus","Medu","Fedu","Mjob","Fjob","guardian")]),
                            ("School context",[c for c in fields if c in ("reason","traveltime")])]
                elif fields is academic:
                    groups=[("Learning progress",[c for c in fields if c in ("G1","G2","studytime","failures")]),
                            ("Learning support",[c for c in fields if c in ("schoolsup","paid","higher")])]
                else:
                    groups=[("Wellbeing and relationships",[c for c in fields if c in ("famsup","activities","romantic","famrel","health")]),
                            ("Daily routine",[c for c in fields if c in ("freetime","goout","Dalc","Walc","absences")])]
                grouped={feature for _,items in groups for feature in items}
                groups.extend([("Additional details",[c for c in fields if c not in grouped])] if any(c not in grouped for c in fields) else [])
                for group_name,group_fields in groups:
                    if not group_fields:
                        continue
                    st.markdown(f'<div class="pivot-form-section">{group_name}</div>',unsafe_allow_html=True)
                    form_cols=st.columns(2,gap="large")
                    for idx,c in enumerate(group_fields):
                        if row is not None: default=row[c]
                        elif c in INPUT_RANGES: default=INPUT_RANGES[c][0]
                        elif c in ("higher","internet"): default="yes"
                        elif c=="school": default="GP"
                        elif c=="sex": default="F"
                        else: default="other"
                        numeric=(pd.api.types.is_numeric_dtype(sample[c]) if len(sample) else isinstance(default,(int,float)))
                        with form_cols[idx%2]:
                            label=FEATURE_LABELS.get(c,c); help_text=f"Model input: {c}"
                            if numeric:
                                bounds=INPUT_RANGES.get(c,(None,None))
                                minimum=float(bounds[0]) if bounds[0] is not None else None
                                maximum=float(bounds[1]) if bounds[1] is not None else None
                                values[c]=st.number_input(label,min_value=minimum,max_value=maximum,value=float(default),step=1.0,key=f"{key}-{c}",help=help_text)
                            else:
                                choices=sorted(sample[c].astype(str).unique().tolist()) if len(sample) else [str(default)]
                                values[c]=st.selectbox(label,choices,index=choices.index(str(default)) if str(default) in choices else 0,key=f"{key}-{c}",help=help_text)
        submitted=st.form_submit_button("Generate prediction",type="primary")
    return submitted,values
def render_prediction(result):
    if not result:return
    with st.container(border=True):
        section_heading("Prediction report", "Returned by the selected model; probabilities retain the model's class ordering.")
        a,b,c=st.columns(3)
        a.metric("Predicted final grade",f"{result['grade']:.1f} / 20")
        b.metric("Performance band",result["class_name"])
        c.metric("Head agreement","Agrees" if not result["disagreement"] else "Review")
        levels=["At Risk","Satisfactory","Strong"]
        dark=st.session_state.get("pivot_theme")=="dark"
        fig=px.bar(x=levels,y=result["probabilities"],color=levels,
            color_discrete_map={"At Risk":"#DA7B93" if dark else "#2E151B","Satisfactory":"#D0A3B0" if dark else "#DA7B93","Strong":"#79AAA4" if dark else "#376E6F"},
            labels={"x":"Performance band","y":"Probability","color":"Class"},title="Classification probabilities")
        fig.update_traces(texttemplate="%{y:.1%}",textposition="outside",cliponaxis=False,
            hovertemplate="%{x}<br>Probability: %{y:.1%}<extra></extra>")
        fig.update_yaxes(range=[0,1.18],tickformat=".0%",title=None)
        st.plotly_chart(chart_theme(fig,330),width="stretch",config={"displaylogo":False,"responsive":True})
        if result["disagreement"]:st.warning("The grade estimate and classification head map to different bands. Both outputs are shown unchanged.")
        if not result.get("history_saved",True):st.info("Prediction generated successfully. MongoDB history is unavailable, so this result was not saved to the student record.")

if page=="Overview":
    intro("PIVOT / Overview","See the signal. Support the student.","A research-oriented view of student performance, prediction quality and cohort needs.")
    df=get_cohort(); c1,c2,c3,c4=st.columns(4)
    rf_ready=all((Path("artifacts/versions")/f"{mode}_rf_{task}"/"pipeline.joblib").exists() for mode in MODES for task in ("regression","classification"))
    selection_path=Path("artifacts/metadata/dnn_selection.json")
    selection=json.loads(selection_path.read_text(encoding="utf-8")) if selection_path.exists() else {}
    dnn_ready=bool(selection) and all(mode in selection and all((Path("artifacts/versions")/f"{mode}_dnn_{selection[mode]}"/name).exists() for name in ("architecture.json","preprocessor.joblib","calibrator.json","weights.index")) for mode in MODES)
    any_artifacts=Path("artifacts/versions").exists() and any(Path("artifacts/versions").iterdir())
    artifact_status="Ready" if rf_ready and dnn_ready else "Partial" if any_artifacts else "Missing"
    c1.metric("Portuguese cohort",f"{len(df):,}" if len(df) else "Unavailable",help="Rows in the loaded UCI Portuguese cohort")
    c2.metric("Dataset columns",f"{len(df.columns)} incl. target" if len(df.columns) else "Unavailable")
    c3.metric("Prediction modes",f"{len(MODES)} independent")
    c4.metric("Model artifacts",artifact_status)
    section_heading("Explore the workspace",eyebrow="WORKSPACES")
    cols=st.columns(3)
    destinations=[("Student insight","Generate an individual student prediction.","Student Prediction"),("What-if simulator","Change inputs and compare model scenarios.","What-if Simulator"),("Cohort lens","Upload a file for batch predictions.","Batch Analytics")]
    for idx,(col,(title,body,destination)) in enumerate(zip(cols,destinations)):
        with col,st.container(border=True):
            st.markdown(f"### {title}"); st.write(body)
            st.button(f"Open {destination}",key=f"open-{idx}",use_container_width=True,on_click=navigate_to,args=(destination,))
    if len(df):
        section_heading("Cohort grade distribution","Actual final Portuguese grade counts from the loaded source cohort.",eyebrow="SOURCE COHORT")
        fig=px.histogram(df,x="G3",nbins=21,color_discrete_sequence=[chart_colors()[0]],labels={"G3":"Final grade (G3)","count":"Students"})
        fig.update_traces(hovertemplate="Final grade: %{x}<br>Students: %{y}<extra></extra>",marker_line_color="#1C3334" if st.session_state.get("pivot_theme")=="dark" else "#FFFFFF",marker_line_width=1)
        fig.update_xaxes(dtick=1)
        st.plotly_chart(chart_theme(fig,360),width="stretch",config={"displaylogo":False,"responsive":True})
    else:empty_state("Cohort data unavailable","Check the dataset files and reload the Overview page.","!")
elif page=="Student":
    intro("PIVOT / Student Profile","Student records","Look up a pseudonymous student profile and its saved prediction history.")
    section_heading("Saved student profiles","Records are loaded from MongoDB Atlas. Only fields stored by the API appear here.",eyebrow="PROFILE DIRECTORY")
    out=call_api("/students",quiet=True)
    if out and out.get("students"):
        students=out["students"]
        ids=[row["student_id"] for row in students if "student_id" in row]
        st.success(f"Atlas connected · {len(ids)} student profiles available")
        if ids:
            selected=st.selectbox("Find a student profile",ids)
            record=next((row for row in students if row.get("student_id")==selected),{})
            left,right=st.columns(2)
            left.metric("Pseudonymous ID",selected)
            right.metric("Cohort",record.get("cohort") or "Not recorded")
            details=call_api(f"/students/{selected}",quiet=True)
            if details:
                history=details.get("recent_predictions",[])
                section_heading("Saved prediction history",f"{len(history)} recent predictions linked to this student.",eyebrow="PROFILE HISTORY")
                if history: render_table(pd.DataFrame(history),width="stretch",hide_index=True)
                else: empty_state("No saved prediction history","Link a Student prediction to this pseudonymous ID to record it when Atlas is available.","◌")
            else: st.info("Prediction history for this profile is unavailable.")
    elif out and out.get("message"):
        empty_state("Atlas is not configured",out["message"],"○")
    elif out:
        empty_state("No student profiles yet","Student profiles appear here after a prediction is saved with a pseudonymous ID.","◎")
    else: st.info("Student profiles are unavailable because MongoDB Atlas cannot be reached. Predictions can still run without profile history.")
elif page=="Student Prediction":
    intro("PIVOT / Student","Individual student intelligence","Generate a performance prediction using the full-information or early-prediction pipeline.")
    section_heading("Prediction configuration","Choose the information available at prediction time and the model to run.",eyebrow="01 / CONFIGURE")
    mode=st.radio("Prediction mode",["full","early"],format_func=lambda x:"Full information (includes G1/G2)" if x=="full" else "Early prediction (excludes G1/G2)",horizontal=True,key="student-mode")
    model=st.radio("Model",["rf","dnn"],format_func=lambda x:"Random Forest baseline" if x=="rf" else "Multi-task DNN",horizontal=True,key="student-model")
    student_id=st.text_input("Pseudonymous student ID (optional)",max_chars=64,placeholder="e.g. learner_001",help="Use a pseudonymous ID; do not enter a student's name.")
    section_heading("Student profile inputs","Complete the relevant fields in each section below.",eyebrow="02 / STUDENT PROFILE")
    sent,values=input_form(mode,"student-form")
    if sent:
        if student_id.strip():
            profile=call_api("/students",{"student_id":student_id.strip()},quiet=True)
            if not profile: st.info("Student profile storage is unavailable. The prediction can still be generated.")
        with st.spinner(f"Running {'Random Forest' if model=='rf' else 'Multi-task DNN'} prediction…"):
            result=call_api("/predict",{"mode":mode,"model":model,"student_id":student_id.strip() or None,"features":values})
        if result: st.session_state["pivot_student_result"]={"result":result,"mode":mode,"model":model}
    latest=st.session_state.get("pivot_student_result")
    if latest:
        st.subheader("Latest prediction")
        st.caption(f"{latest['mode'].title()} mode · {'Random Forest' if latest['model']=='rf' else 'Multi-task DNN'}")
        render_prediction(latest["result"])
elif page=="What-if Simulator":
    intro("PIVOT / What-if Simulator","Explore a scenario","Set a baseline, change one or more inputs, and compare model outputs. This is a model scenario, not a causal intervention estimate.")
    if "pivot_sim_base" not in st.session_state:
        st.subheader("Step 1 · Set the baseline")
        mode=st.radio("Prediction mode",["full","early"],format_func=lambda x:"Full information" if x=="full" else "Early prediction",horizontal=True,key="sim-mode")
        model=st.radio("Model",["rf","dnn"],format_func=lambda x:"Random Forest" if x=="rf" else "Multi-task DNN",horizontal=True,key="sim-model")
        sent,values=input_form(mode,"sim-form")
        if sent: st.session_state["pivot_sim_base"]={"mode":mode,"model":model,"features":values,"id":uuid.uuid4().hex}; st.rerun()
    else:
        base=st.session_state["pivot_sim_base"]; values=base["features"]; choices=list(values)
        st.subheader("Step 2 · Change scenario inputs")
        st.caption(f"Baseline: {base['mode'].title()} prediction with {('Random Forest' if base['model']=='rf' else 'Multi-task DNN')}. Select any model input to vary it.")
        features=st.multiselect("Inputs to change",choices,default=[choices[0]] if choices else [],format_func=lambda c:FEATURE_LABELS.get(c,c),help="Choose one or more available model inputs.")
        df=get_cohort()
        changes={}
        if features:
            change_cols=st.columns(2,gap="large")
            for idx,feature in enumerate(features):
                with change_cols[idx%2]:
                    if isinstance(values[feature],(int,float)):
                        bounds=INPUT_RANGES.get(feature,(None,None))
                        minimum=float(bounds[0]) if bounds[0] is not None else None
                        maximum=float(bounds[1]) if bounds[1] is not None else None
                        changes[feature]=st.number_input(f"{FEATURE_LABELS.get(feature,feature)} · scenario value",min_value=minimum,max_value=maximum,value=float(values[feature]),step=1.0,key=f"scenario-{base['id']}-{feature}")
                    else:
                        opts=sorted(df[feature].astype(str).unique().tolist()) if len(df) and feature in df else [str(values[feature])]
                        current=str(values[feature]); default_idx=opts.index(current) if current in opts else 0
                        changes[feature]=st.selectbox(f"{FEATURE_LABELS.get(feature,feature)} · scenario value",opts,index=default_idx,key=f"scenario-{base['id']}-{feature}")
        compare_col,reset_col=st.columns([2,1])
        with compare_col: compare=st.button("Compare baseline and scenario",type="primary",disabled=not features,use_container_width=True)
        with reset_col: reset=st.button("Start over",use_container_width=True)
        if reset:
            st.session_state.pop("pivot_sim_base",None); st.session_state.pop("pivot_sim_result",None); st.session_state.pop("pivot_sim_changes",None); st.rerun()
        if compare:
            with st.spinner("Comparing the baseline and scenario with the selected model…"):
                st.session_state["pivot_sim_result"]=call_api("/scenario",{"base":{"mode":base["mode"],"model":base["model"],"features":values},"changes":changes})
            st.session_state["pivot_sim_changes"]=changes
        out=st.session_state.get("pivot_sim_result")
        if out:
            st.subheader("Step 3 · Compare model outputs")
            baseline,scenario=out["baseline"],out["scenario"]
            left,middle,right=st.columns(3)
            left.metric("Baseline grade",f"{baseline['grade']:.1f} / 20",help=baseline["class_name"])
            middle.metric("Scenario grade",f"{scenario['grade']:.1f} / 20",delta=f"{out['grade_delta']:+.1f} points",help=scenario["class_name"])
            right.metric("Scenario performance band",scenario["class_name"])
            saved_changes=st.session_state.get("pivot_sim_changes",{})
            if saved_changes:
                st.markdown("**Inputs changed in this comparison**")
                render_table(pd.DataFrame([{"Input":FEATURE_LABELS.get(name,name),"Baseline":values[name],"Scenario":value} for name,value in saved_changes.items()]),hide_index=True,width="stretch")
            levels=["At Risk","Satisfactory","Strong"]
            palette=chart_colors()
            fig=px.bar(x=levels*2,y=baseline["probabilities"]+scenario["probabilities"],color=["Baseline"]*3+["Scenario"]*3,barmode="group",color_discrete_sequence=[palette[0],palette[3]],labels={"x":"Performance band","y":"Probability","color":"Inputs"},title="Baseline and scenario probabilities")
            fig.update_yaxes(tickformat=".0%",range=[0,1.08],title=None)
            fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y:.1%}<extra></extra>")
            st.plotly_chart(chart_theme(fig,350),width="stretch",config={"displaylogo":False,"responsive":True})
            st.caption(out["interpretation"])
elif page=="Educator":
    intro("PIVOT / Educator","Cohort overview","Recent predictions and aggregate signals, when MongoDB Atlas is configured.")
    section_heading("Student records","Profiles and prediction history saved by the existing API.",eyebrow="ATLAS WORKSPACE")
    out=call_api("/students",quiet=True)
    if out and out.get("students"):
        st.success(f"Atlas connected · {len(out['students'])} student profiles loaded")
        render_table(pd.DataFrame(out["students"]),width="stretch")
        ids=[row["student_id"] for row in out["students"] if "student_id" in row]
        if ids:
            selected=st.selectbox("Student profile",ids)
            details=call_api(f"/students/{selected}",quiet=True)
            if details:
                section_heading("Profile detail",eyebrow="SELECTED STUDENT")
                st.json(details,expanded=False)
            else: st.info("This profile could not be loaded from MongoDB Atlas. Prediction features remain available.")
    elif out and out.get("message"):
        empty_state("Atlas is not configured",out["message"],"○")
    elif out:
        st.success("Atlas connected")
        empty_state("No saved student records yet","Generate a Student prediction with a pseudonymous ID to create a profile.","◎")
    else:st.info("Student records are unavailable because MongoDB Atlas cannot be reached. Student and batch predictions can still run; profile and history views need Atlas.")
elif page=="Batch Analytics":
    intro("PIVOT / Batch analytics","Read a cohort file","Upload CSV records with the eligible feature columns for batch predictions.")
    section_heading("Configure batch run","The uploaded CSV must contain the selected pipeline's feature columns.",eyebrow="01 / CONFIGURE")
    mode_col,model_col=st.columns(2)
    mode=mode_col.radio("Prediction mode",["full","early"],format_func=lambda x:"Full information" if x=="full" else "Early prediction",horizontal=True,key="batch-mode")
    model=model_col.radio("Model",["rf","dnn"],format_func=lambda x:"Random Forest" if x=="rf" else "Multi-task DNN",horizontal=True,key="batch-model")
    section_heading("Upload a cohort CSV","Choose a CSV file or use the template to match the required columns.",eyebrow="02 / UPLOAD")
    f=st.file_uploader("Drop your cohort file here or browse",type=["csv"],label_visibility="visible",help="CSV format supported")
    template=pd.DataFrame(columns=MODES[mode]).to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV template",template,file_name=f"pivot_{mode}_input_template.csv",mime="text/csv")
    if not f:empty_state("No cohort file selected","Upload a CSV with the eligible columns for the selected prediction mode.","⇧")
    if f:
        upload_id=hashlib.sha256(f.getvalue()).hexdigest()[:16]
        try:
            batch=pd.read_csv(f)
            st.caption(f"{len(batch):,} rows · {len(batch.columns):,} columns · {int(batch.isna().sum().sum()):,} missing values")
            render_table(batch.head(8),width="stretch")
            missing=set(MODES[mode])-set(batch.columns)
            if missing: st.error(f"Missing required columns: {', '.join(sorted(missing))}")
            elif batch.empty: st.warning("The uploaded CSV has headers but no student rows.")
            else:
                st.success(f"CSV validated · {len(batch):,} records ready for prediction")
                if st.button("Predict cohort",type="primary"):
                    with st.spinner(f"Running batch prediction with {'Random Forest' if model=='rf' else 'Multi-task DNN'}…"):
                        out=call_api("/predict/batch",{"mode":mode,"model":model,"records":batch[MODES[mode]].to_dict("records")})
                    if out: st.session_state["pivot_batch_result"]={"upload_id":upload_id,"mode":mode,"model":model,"predictions":out["predictions"]}
        except (UnicodeDecodeError,pd.errors.ParserError) as exc:
            st.error(f"Could not read this CSV: {exc}")
        latest_batch=st.session_state.get("pivot_batch_result")
        if latest_batch and latest_batch["upload_id"]==upload_id and latest_batch["mode"]==mode and latest_batch["model"]==model:
            section_heading("Prediction results","Actual model outputs for each uploaded record.",eyebrow="03 / COMPLETE")
            st.caption(f"{len(latest_batch['predictions']):,} student records · {model.upper()} · {mode} mode")
            results_frame=pd.DataFrame(latest_batch["predictions"])
            render_table(results_frame,width="stretch")
            st.download_button("Download prediction results",results_frame.to_csv(index=False).encode("utf-8"),file_name="pivot_batch_predictions.csv",mime="text/csv")
elif page=="Research Lab":
    intro("PIVOT / Research lab","Model evidence","Evaluation results from the recorded training runs, with development analyses and subgroup views.")
    results=load_results(); report_dir=Path("reports/experiments")
    mlflow_status=results.get("mlflow_status",{})
    if mlflow_status:st.caption(f"MLflow tracking · {mlflow_status.get('status','status unavailable')} · {mlflow_status.get('runs',0)} recorded runs")
    evidence_tab,analysis_tab,explain_tab=st.tabs(["Model evidence","Feature & subgroup analysis","Explanations & run record"])
    with evidence_tab:
        section_heading("Evaluation comparison","Held-out and recorded metrics from the existing experiment results.",eyebrow="MODEL EVIDENCE")
        rows=[]
        for mode in MODES:
            rf_reg=results.get(f"{mode}_rf_regression",{}); rf_cls=results.get(f"{mode}_rf_classification",{})
            rows.append({"Model":"Random Forest","Mode":mode.title(),"MAE":rf_reg.get("mae"),"RMSE":rf_reg.get("rmse"),"R²":rf_reg.get("r2"),"Accuracy":rf_cls.get("accuracy"),"Macro F1":rf_cls.get("macro_f1")})
            dnn_key=next((key for key in results if key.startswith(f"{mode}_dnn_")),None)
            dnn=results.get(dnn_key,{}) if dnn_key else {}
            reg=dnn.get("regression",{}); cls=dnn.get("classification",{})
            rows.append({"Model":"Multi-task DNN","Mode":mode.title(),"MAE":reg.get("mae"),"RMSE":reg.get("rmse"),"R²":reg.get("r2"),"Accuracy":cls.get("accuracy"),"Macro F1":cls.get("macro_f1")})
        available=[row for row in rows if row["MAE"] is not None or row["Accuracy"] is not None]
        if available:render_table(pd.DataFrame(available).round(3),hide_index=True,width="stretch")
        else:empty_state("No evaluation results","Run the training command to create model evidence.","∅")
        group_path=report_dir/"feature_groups.json"
        if group_path.exists():
            group_data=json.loads(group_path.read_text(encoding="utf-8")); group_rows=[]
            for name,item in group_data.items():
                metrics=item.get("metrics",{}); parts=name.split("_")
                group_rows.append({"Mode":parts[0].title(),"Feature group":" ".join(parts[1:-1]).title(),"Task":parts[-1].title(),"MAE":metrics.get("mae"),"RMSE":metrics.get("rmse"),"R²":metrics.get("r2"),"Accuracy":metrics.get("accuracy"),"Macro F1":metrics.get("macro_f1")})
            with st.expander("Feature-group experiment comparison"):
                render_table(pd.DataFrame(group_rows).round(3),hide_index=True,width="stretch")
        for filename,title in [("feature_groups.json","Feature-group experiment records"),("ablation_results.json","Architecture validation ablation"),("single_task_results.json","Single-task vs multi-task validation")]:
            report=report_dir/filename
            if report.exists():
                report_data=json.loads(report.read_text(encoding="utf-8"))
                if filename=="ablation_results.json":
                    ablation_rows=[]
                    for key,value in report_data.items():
                        reg=value.get("validation_regression",{}); cls=value.get("validation_classification",{})
                        ablation_rows.append({"Variant":key,"MAE":reg.get("mae"),"RMSE":reg.get("rmse"),"R²":reg.get("r2"),"Accuracy":cls.get("accuracy"),"Macro F1":cls.get("macro_f1")})
                    with st.expander(title):
                        render_table(pd.DataFrame(ablation_rows).round(3),hide_index=True,width="stretch")
                        st.json(report_data,expanded=False)
                elif filename=="single_task_results.json":
                    task_rows=[]
                    for key,value in report_data.items():
                        metric=value.get("validation",{}); parts=key.split("_")
                        task_rows.append({"Mode":parts[0].title(),"Task":parts[1].title(),"MAE":metric.get("mae"),"RMSE":metric.get("rmse"),"R²":metric.get("r2"),"Accuracy":metric.get("accuracy"),"Macro F1":metric.get("macro_f1")})
                    with st.expander(title):
                        render_table(pd.DataFrame(task_rows).round(3),hide_index=True,width="stretch")
                        st.json(report_data,expanded=False)
                else:
                    with st.expander(title):st.json(report_data,expanded=False)
    with analysis_tab:
        section_heading("Development feature rankings","Recorded mutual information and permutation scores from the development split.",eyebrow="FEATURE ANALYSIS")
        feature_path=report_dir/"feature_selection.json"
        if feature_path.exists():
            feature_data=json.loads(feature_path.read_text(encoding="utf-8"))
            selector_col,task_col,score_col=st.columns(3)
            rank_mode=selector_col.selectbox("Pipeline",["full","early"],format_func=lambda x:x.title(),key="rank-mode")
            rank_task=task_col.selectbox("Task",["regression","classification"],format_func=lambda x:x.title(),key="rank-task")
            score_type=score_col.selectbox("Ranking method",["mutual_information_top20","permutation_top20"],format_func=lambda x:"Mutual information" if x.startswith("mutual") else "Permutation importance",key="rank-score")
            ranking=feature_data[rank_mode][rank_task][score_type]
            score_key="score" if score_type.startswith("mutual") else "score_mean"
            rank_df=pd.DataFrame([{"Feature":item["feature"],"Score":item[score_key],"SD":item.get("score_std",0)} for item in ranking[:15]])
            rank_df=rank_df.sort_values("Score",ascending=True)
            rank_fig=px.bar(rank_df,x="Score",y="Feature",orientation="h",color_discrete_sequence=[chart_colors()[0]],error_x="SD" if score_type.startswith("permutation") else None,labels={"Score":"Recorded score","Feature":"Feature"},title=f"{rank_mode.title()} · {rank_task.title()} · {'Mutual information' if score_type.startswith('mutual') else 'Permutation importance'}")
            rank_fig.update_traces(hovertemplate="%{y}<br>Score: %{x:.3f}<extra></extra>")
            st.plotly_chart(chart_theme(rank_fig,max(360,len(rank_df)*26)),width="stretch",config={"displaylogo":False,"responsive":True})
            with st.expander("Full feature ranking records"):st.json(feature_data,expanded=False)
        else:empty_state("Feature rankings unavailable","No feature-selection report was found.","∅")
        fairness_path=report_dir/"fairness.json"
        if fairness_path.exists():
            section_heading("Subgroup performance · Random Forest","Held-out subgroup summaries; group sizes are shown alongside metrics.",eyebrow="SUBGROUP ANALYSIS")
            fdata=json.loads(fairness_path.read_text(encoding="utf-8")); frows=[{"Mode":m.title(),**row} for m,items in fdata.items() for row in items]
            render_table(pd.DataFrame(frows).rename(columns={"feature":"Feature","group":"Group","n":"N","mae":"MAE","recall_macro":"Macro recall"}).round(3),hide_index=True,width="stretch")
        interactions_path=report_dir/"interactions.json"
        if interactions_path.exists():
            section_heading("Pairwise partial-dependence probe","Largest recorded pairwise interaction scores.",eyebrow="INTERACTIONS")
            interaction_data=json.loads(interactions_path.read_text(encoding="utf-8"))
            interaction_rows=[{"Mode":mode.title(),"Feature pair":" × ".join(item["features"]),"Interaction RMS":item["pdp_interaction_rms"]} for mode,items in interaction_data.items() for item in items]
            if interaction_rows:
                interaction_df=pd.DataFrame(interaction_rows).sort_values("Interaction RMS")
                palette=chart_colors()
                interaction_fig=px.bar(interaction_df,x="Interaction RMS",y="Feature pair",color="Mode",orientation="h",color_discrete_sequence=[palette[0],palette[2]],labels={"Interaction RMS":"Partial-dependence interaction RMS"},title="Recorded pairwise interaction scores")
                interaction_fig.update_traces(hovertemplate="%{y}<br>RMS: %{x:.4f}<extra></extra>")
                st.plotly_chart(chart_theme(interaction_fig,max(350,len(interaction_df)*21)),width="stretch",config={"displaylogo":False,"responsive":True})
            with st.expander("View interaction records"):st.json(interaction_data,expanded=False)
    with explain_tab:
        section_heading("Local explanation example · LIME","Recorded local perturbation explanation and its caution statement.",eyebrow="EXPLAINABILITY")
        lime_path=report_dir/"lime_full_row0.json"
        if lime_path.exists():
            lime=json.loads(lime_path.read_text(encoding="utf-8"))
            if lime.get("explanation"):
                lime_df=pd.DataFrame(lime["explanation"])
                if {"rule","weight"}.issubset(lime_df.columns):
                    lime_df=lime_df.sort_values("weight")
                    lime_scale=["#DA7B93","#1C3334","#79AAA4"] if st.session_state.get("pivot_theme")=="dark" else ["#2E151B","#F0E7E7","#376E6F"]
                    lime_fig=px.bar(lime_df,x="weight",y="rule",orientation="h",color="weight",color_continuous_scale=lime_scale,labels={"weight":"Local explanation weight","rule":"Feature condition"},title="Recorded LIME explanation")
                    lime_fig.update_coloraxes(showscale=False)
                    st.plotly_chart(chart_theme(lime_fig,max(320,len(lime_df)*28)),width="stretch",config={"displaylogo":False,"responsive":True})
            st.caption(lime.get("caution",""))
            with st.expander("View raw LIME record"):st.json(lime,expanded=False)
        else:empty_state("LIME example unavailable","No local explanation record was found.","∅")
        section_heading("Full run record","Expandable source record from the completed training run.",eyebrow="EXPERIMENT RECORD")
        if results:st.json(results,expanded=False)
        else:empty_state("No training run record","Run training to populate experiment metadata.","∅")

