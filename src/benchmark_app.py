"""
Interface Streamlit pour visualiser les résultats du benchmark RAG
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

from src.benchmark import RAGBenchmark


st.set_page_config(
    page_title="RAG Benchmark Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RAG Performance Benchmark Dashboard")
st.markdown("Comparer les performances des différents LLMs et stratégies RAG")

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

# Charger ou exécuter un benchmark
benchmark_action = st.sidebar.radio(
    "Action",
    ["📂 Charger résultats existants", "🚀 Exécuter nouveau benchmark"]
)

if benchmark_action == "🚀 Exécuter nouveau benchmark":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Paramètres du benchmark")
    
    # Sélection des LLMs
    llms_available = ["openai", "ollama", "gemini"]
    selected_llms = st.sidebar.multiselect(
        "LLMs à tester",
        llms_available,
        default=["openai"]
    )
    
    # Sélection des stratégies
    strategies_available = ["simple", "secure", "hybrid", "modular"]
    selected_strategies = st.sidebar.multiselect(
        "Stratégies RAG à tester",
        strategies_available,
        default=["simple", "secure"]
    )
    
    # Nombre de questions
    num_questions = st.sidebar.slider(
        "Nombre de questions à tester",
        min_value=1,
        max_value=10,
        value=3
    )
    
    if st.sidebar.button("▶️ Lancer le benchmark", type="primary"):
        with st.spinner("Exécution du benchmark en cours..."):
            benchmark = RAGBenchmark()
            
            # Prendre les N premières questions
            question_ids = [i+1 for i in range(num_questions)]
            
            results_df = benchmark.run_full_benchmark(
                llms_to_test=selected_llms,
                strategies_to_test=selected_strategies,
                questions_to_test=question_ids
            )
            
            # Sauvegarder les résultats
            benchmark.save_results()
            benchmark.save_results_json()
            
            st.session_state['benchmark_results'] = results_df
            st.success(f"✅ Benchmark terminé ! {len(results_df)} tests exécutés")

else:
    # Charger les résultats existants
    results_path = "reports/benchmark_results.csv"
    
    if Path(results_path).exists():
        results_df = pd.read_csv(results_path)
        st.session_state['benchmark_results'] = results_df
        st.sidebar.success(f"✅ Résultats chargés: {len(results_df)} tests")
    else:
        st.sidebar.warning("⚠️ Aucun résultat trouvé. Lancez un nouveau benchmark.")
        results_df = None

# Affichage des résultats
if 'benchmark_results' in st.session_state and st.session_state['benchmark_results'] is not None:
    df = st.session_state['benchmark_results']
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Vue d'ensemble", 
        "⏱️ Performances", 
        "💰 Coûts", 
        "📋 Détails"
    ])
    
    with tab1:
        st.header("Vue d'ensemble des résultats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total tests", len(df))
        with col2:
            success_rate = (df['status'] == 'success').mean() * 100
            st.metric("Taux de succès", f"{success_rate:.1f}%")
        with col3:
            avg_time = df['total_time'].mean()
            st.metric("Temps moyen", f"{avg_time:.2f}s")
        with col4:
            avg_tokens = df['tokens_estimated'].mean()
            st.metric("Tokens moyens", f"{avg_tokens:.0f}")
        
        st.markdown("---")
        
        # Résumé par LLM et stratégie
        summary = df.groupby(['llm', 'strategy']).agg({
            'total_time': ['mean', 'min', 'max'],
            'tokens_estimated': 'mean',
            'num_documents': 'mean'
        }).round(3)
        
        st.subheader("📊 Résumé par configuration")
        st.dataframe(summary, use_container_width=True)
    
    with tab2:
        st.header("⏱️ Analyse des performances")
        
        # Graphique: Temps total par LLM et stratégie
        fig1 = px.bar(
            df.groupby(['llm', 'strategy'])['total_time'].mean().reset_index(),
            x='llm',
            y='total_time',
            color='strategy',
            title="Temps de réponse moyen par LLM et stratégie",
            labels={'total_time': 'Temps (secondes)', 'llm': 'LLM'},
            barmode='group'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Décomposition du temps
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = px.box(
                df,
                x='llm',
                y='retrieval_time',
                color='strategy',
                title="Distribution du temps de récupération",
                labels={'retrieval_time': 'Temps (secondes)', 'llm': 'LLM'}
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = px.box(
                df,
                x='llm',
                y='llm_time',
                color='strategy',
                title="Distribution du temps de génération",
                labels={'llm_time': 'Temps (secondes)', 'llm': 'LLM'}
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # Scatter plot: Temps vs nombre de documents
        fig4 = px.scatter(
            df,
            x='num_documents',
            y='total_time',
            color='llm',
            symbol='strategy',
            size='tokens_estimated',
            title="Temps total vs Nombre de documents récupérés",
            labels={
                'num_documents': 'Nombre de documents',
                'total_time': 'Temps total (secondes)'
            },
            hover_data=['question']
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        st.header("💰 Analyse des coûts")
        
        # Estimation des coûts (approximation)
        COST_PER_1K_TOKENS = {
            'openai': 0.0015,  # GPT-4o-mini
            'ollama': 0.0,     # Gratuit (local)
            'gemini': 0.0001   # Gemini Flash
        }
        
        df['estimated_cost'] = df.apply(
            lambda row: (row['tokens_estimated'] / 1000) * COST_PER_1K_TOKENS.get(row['llm'], 0),
            axis=1
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Coût total par LLM
            cost_by_llm = df.groupby('llm')['estimated_cost'].sum().reset_index()
            fig5 = px.bar(
                cost_by_llm,
                x='llm',
                y='estimated_cost',
                title="Coût total estimé par LLM",
                labels={'estimated_cost': 'Coût ($)', 'llm': 'LLM'},
                color='llm'
            )
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            # Tokens utilisés par stratégie
            tokens_by_strategy = df.groupby('strategy')['tokens_estimated'].mean().reset_index()
            fig6 = px.bar(
                tokens_by_strategy,
                x='strategy',
                y='tokens_estimated',
                title="Tokens moyens par stratégie",
                labels={'tokens_estimated': 'Tokens', 'strategy': 'Stratégie'},
                color='strategy'
            )
            st.plotly_chart(fig6, use_container_width=True)
        
        st.markdown("---")
        
        # Tableau des coûts
        cost_summary = df.groupby(['llm', 'strategy']).agg({
            'tokens_estimated': 'mean',
            'estimated_cost': 'sum'
        }).round(4)
        
        st.subheader("💵 Résumé des coûts")
        st.dataframe(cost_summary, use_container_width=True)
        
        total_cost = df['estimated_cost'].sum()
        st.metric("Coût total du benchmark", f"${total_cost:.4f}")
    
    with tab4:
        st.header("📋 Détails des tests")
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_llm = st.multiselect(
                "Filtrer par LLM",
                df['llm'].unique(),
                default=df['llm'].unique()
            )
        
        with col2:
            filter_strategy = st.multiselect(
                "Filtrer par stratégie",
                df['strategy'].unique(),
                default=df['strategy'].unique()
            )
        
        with col3:
            filter_status = st.multiselect(
                "Filtrer par statut",
                df['status'].unique(),
                default=df['status'].unique()
            )
        
        # Appliquer les filtres
        filtered_df = df[
            (df['llm'].isin(filter_llm)) &
            (df['strategy'].isin(filter_strategy)) &
            (df['status'].isin(filter_status))
        ]
        
        # Afficher le tableau
        st.dataframe(
            filtered_df[[
                'question_id', 'llm', 'strategy', 'total_time', 
                'num_documents', 'tokens_estimated', 'status'
            ]].sort_values('total_time'),
            use_container_width=True
        )
        
        # Afficher les réponses individuelles
        st.markdown("---")
        st.subheader("🔍 Détails d'une réponse")
        
        selected_idx = st.selectbox(
            "Sélectionner un test",
            range(len(filtered_df)),
            format_func=lambda i: f"Q{filtered_df.iloc[i]['question_id']} - {filtered_df.iloc[i]['llm']} + {filtered_df.iloc[i]['strategy']}"
        )
        
        if selected_idx is not None:
            row = filtered_df.iloc[selected_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Question:**")
                st.info(row['question'])
                
                st.markdown("**Configuration:**")
                st.write(f"- LLM: `{row['llm']}`")
                st.write(f"- Stratégie: `{row['strategy']}`")
                st.write(f"- Documents trouvés: {row['num_documents']}")
            
            with col2:
                st.markdown("**Performance:**")
                st.write(f"- Temps total: {row['total_time']:.3f}s")
                st.write(f"- Temps récupération: {row['retrieval_time']:.3f}s")
                st.write(f"- Temps génération: {row['llm_time']:.3f}s")
                st.write(f"- Tokens estimés: {row['tokens_estimated']:.0f}")
            
            st.markdown("**Réponse:**")
            st.success(row['answer'])

else:
    st.info("👈 Utilisez le menu latéral pour charger des résultats existants ou lancer un nouveau benchmark")

# Footer
st.markdown("---")
st.caption("📊 RAG Benchmark Dashboard - Comparez les performances de vos systèmes RAG")
