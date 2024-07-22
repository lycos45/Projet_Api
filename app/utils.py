# app/utils.py
def update_prompt_price(prompt_id, cur):
    try:
        # Calculer la moyenne des notes
        cur.execute("SELECT AVG(score) FROM notes WHERE prompt_id = %s", (prompt_id,))
        avg_score = cur.fetchone()[0]

        if avg_score is None:
            avg_score = 0

        # Recalculer le prix
        new_price = 1000 * (1 + avg_score)

        # Mettre à jour le prix dans la base de données
        cur.execute(
            "UPDATE prompts SET price = %s WHERE id = %s",
            (new_price, prompt_id)
        )
    except Exception as e:
        raise Exception(f"Failed to update prompt price: {str(e)}")
    
    

def count_votes_and_update_status(prompt_id, cur):
    cur.execute("""
        SELECT 
            SUM(
                CASE 
                    WHEN gm.user_id IS NOT NULL THEN 2 * v.vote_value 
                    ELSE v.vote_value 
                END
            ) AS vote_points
        FROM votes v
        LEFT JOIN group_members gm ON v.user_id = gm.user_id
        WHERE v.prompt_id = %s
        GROUP BY v.prompt_id
    """, (prompt_id,))
    result = cur.fetchone()
    vote_points = result[0] if result else 0

    if vote_points >= 6:
        cur.execute("UPDATE prompts SET status = 'Activé' WHERE id = %s", (prompt_id,))
        update_prompt_price(prompt_id, cur)  # Recalculate the price


