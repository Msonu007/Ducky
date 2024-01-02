import streamlit as st


def show() -> None:
	with st.sidebar:
		st.markdown(f"""
			<a href="/" style="color:black;text-decoration: none;">
				<div style="display:table;margin-top:-16rem;margin-left:0%;">
					<img src="/app/static/logo.png" width="30"><span>Ducky</span>
					<span style="font-size: 0.8em; color: grey">&nbsp;&nbsp;v0.1.0</span>
					<br>
					<span style="font-size: 0.8em"> your AI-powered software developer assistant</span>
				</div>
			</a>
			<br>
				""", unsafe_allow_html=True)

		reload_button = st.button("↪︎  Reload Page")
		if reload_button:
			st.session_state.clear()
			st.experimental_rerun()

