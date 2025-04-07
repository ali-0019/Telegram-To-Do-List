import sqlite3

def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (user_id INTEGER, 
                  task_id INTEGER,
                  task_text TEXT, 
                  due_date TEXT,
                  PRIMARY KEY (user_id, task_id))''')
    conn.commit()
    conn.close()

def add_task(user_id, task_text, due_date):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    
    # Get the highest task_id for this user
    c.execute("SELECT MAX(task_id) FROM tasks WHERE user_id = ?", (user_id,))
    max_id = c.fetchone()[0]
    next_id = 1 if max_id is None else max_id + 1
    
    # Insert with the next sequential ID
    c.execute("INSERT INTO tasks (user_id, task_id, task_text, due_date) VALUES (?, ?, ?, ?)", 
             (user_id, next_id, task_text, due_date))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT task_id, task_text, due_date FROM tasks WHERE user_id = ?", (user_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def delete_task(user_id, task_id):
    try:
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        
        # Delete the task
        c.execute("DELETE FROM tasks WHERE user_id = ? AND task_id = ?", (user_id, task_id))
        
        if c.rowcount > 0:
            # Update remaining task IDs to ensure sequential ordering
            c.execute("""
                UPDATE tasks 
                SET task_id = (
                    SELECT COUNT(*) 
                    FROM tasks t2 
                    WHERE t2.user_id = tasks.user_id AND t2.task_id <= tasks.task_id
                )
                WHERE user_id = ? AND task_id > ?
            """, (user_id, task_id))
            
            conn.commit()
            conn.close()
            return True
            
        conn.close()
        return False
        
    except sqlite3.Error:
        if 'conn' in locals():
            conn.close()
        return False

def edit_task(user_id, task_id, new_text):
    try:
        conn = sqlite3.connect('todo.db')  # Changed from 'tasks.db' to 'todo.db'
        c = conn.cursor()
        
        # Check if task exists and belongs to user
        c.execute('SELECT task_id FROM tasks WHERE task_id = ? AND user_id = ?', (task_id, user_id))
        if not c.fetchone():
            conn.close()
            return False
        
        # Update the task text
        c.execute('UPDATE tasks SET task_text = ? WHERE task_id = ? AND user_id = ?', 
                 (new_text, task_id, user_id))
        conn.commit()
        
        # Verify the update was successful
        if c.rowcount > 0:
            conn.close()
            return True
        
        conn.close()
        return False
        
    except sqlite3.Error:
        if 'conn' in locals():
            conn.close()
        return False