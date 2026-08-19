"""
pages/5_Content_AI.py

Same shared-helper pattern as Email AI. Social Media Generator needs a
platform selector alongside the free-text input, which is why it doesn't
go through run_prompt_tab's default path — the platform choice is passed
in as prompt_prefix so it's part of the LLM call without cluttering the
input box itself.
"""

import streamlit as st
from core.auth import require_login
from core.prompt_module import run_prompt_tab

MODULE_NAME = "content_ai"

require_login()
user_id = st.session_state["user_id"]

st.title("Content AI")

tab_blog, tab_social, tab_marketing = st.tabs(["Blog Generator", "Social Media Generator", "Marketing Copy"])

with tab_blog:
    st.caption("Give me a topic or rough outline — I'll write a full blog post.")
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="blog",
        system_prompt=(
            "You are a skilled blog writer. Write a well-structured, engaging blog post based "
            "on the user's topic or outline. Use clear headings (##), short paragraphs, and a "
            "natural, readable tone. Aim for 500-800 words unless the user specifies a length."
        ),
        user_id=user_id,
        input_label="Topic or outline",
        placeholder="e.g. Why skincare routines should change with the seasons",
        height=140,
    )

with tab_social:
    st.caption("Pick a platform and describe the post — I'll write a platform-ready caption.")
    platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Twitter/X", "Facebook", "TikTok"])
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="social",
        system_prompt=(
            "You are a social media copywriter. Write a platform-ready post for the specified "
            "platform, matching that platform's typical tone and length conventions (e.g. "
            "Instagram: punchy + hashtags, LinkedIn: professional + no excessive hashtags, "
            "Twitter/X: under 280 characters). Include relevant hashtags where appropriate."
        ),
        user_id=user_id,
        input_label="What's the post about?",
        placeholder="e.g. Announcing our new embroidered collection launch",
        height=120,
        prompt_prefix=f"Platform: {platform}",
    )

with tab_marketing:
    st.caption("Describe the product/service and audience — I'll write persuasive copy.")
    copy_type = st.selectbox("Copy type", ["Ad copy", "Landing page section", "Product description", "Email campaign"])
    run_prompt_tab(
        module_name=MODULE_NAME,
        sub_feature="marketing_copy",
        system_prompt=(
            "You are a persuasive marketing copywriter. Write compelling copy of the specified "
            "type, focused on benefits (not just features), with a clear call to action. Match "
            "the tone to the product described — don't default to generic corporate language."
        ),
        user_id=user_id,
        input_label="Describe the product/service, target audience, and goal",
        placeholder="e.g. Embroidered Asian ethnic wear, targeting women 20-35, goal: drive Instagram traffic to the shop",
        height=140,
        prompt_prefix=f"Copy type: {copy_type}",
    )