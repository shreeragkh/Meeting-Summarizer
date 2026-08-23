"""Streamlit entrypoint. Wires together transcriber, summarizer, and database."""

import os
import tempfile
import streamlit as st

from .config import config
from .transcriber import transcribe_audio, TranscriptionError
from .summarizer import summarize_transcript
from .database import init_db, save_meeting, get_all_meetings, delete_meeting


def render_action_items(action_items: list[dict]) -> None:
    if not action_items:
        st.write("No action items identified.")
        return
    for item in action_items:
        st.markdown(
            f"- **{item.get('task', 'N/A')}** "
            f"— Owner: {item.get('owner', 'Unassigned')} "
            f"— Deadline: {item.get('deadline', 'Not specified')}"
        )


def render_decisions(decisions: list[str]) -> None:
    if not decisions:
        st.write("No decisions identified.")
        return
    for d in decisions:
        st.markdown(f"- {d}")


def main() -> None:
    st.set_page_config(page_title="Meeting Summarizer", page_icon="📝", layout="wide")
    config.validate()
    init_db()

    st.title("📝 Meeting Summarizer")
    st.caption("Upload a meeting recording to get a transcript, summary, and action items.")

    tab_upload, tab_history = st.tabs(["Upload & Process", "Past Meetings"])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload meeting audio or video",
            type=["mp3", "wav", "m4a", "mp4", "mov", "mkv"],
        )

        if uploaded_file and st.button("Process Meeting", type="primary"):
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                with st.spinner("Transcribing audio..."):
                    transcript = transcribe_audio(tmp_path, uploaded_file.name)

                with st.spinner("Generating summary and action items..."):
                    result = summarize_transcript(transcript)

                meeting_id = save_meeting(
                    filename=uploaded_file.name,
                    transcript=transcript,
                    summary=result.get("summary", ""),
                    decisions=result.get("decisions", []),
                    action_items=result.get("action_items", []),
                )

                st.success(f"Meeting processed and saved (ID: {meeting_id})")

                st.subheader("Summary")
                st.write(result.get("summary", "No summary generated."))

                st.subheader("Key Decisions")
                render_decisions(result.get("decisions", []))

                st.subheader("Action Items")
                render_action_items(result.get("action_items", []))

                with st.expander("View full transcript"):
                    st.write(transcript)

            except TranscriptionError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong while processing: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    with tab_history:
        st.subheader("Past Meetings")
        meetings = get_all_meetings()

        if not meetings:
            st.info("No meetings processed yet.")
        else:
            for m in meetings:
                label = f"{m['filename']} — {m['created_at'].strftime('%Y-%m-%d %H:%M')}"
                with st.expander(label):
                    st.write("**Summary:**", m["summary"])
                    st.write("**Decisions:**")
                    render_decisions(m["decisions"] or [])
                    st.write("**Action Items:**")
                    render_action_items(m["action_items"] or [])

                    if st.button("Delete this meeting", key=f"delete_{m['id']}"):
                        delete_meeting(m["id"])
                        st.rerun()


if __name__ == "__main__":
    main()