import os

content = r"""{% extends 'generator/base.html' %}

{% block content %}
<div class="research-container">
    <div class="header-section">
        <h1 class="premium-title">Centro de Investigacion IA</h1>
        <p class="premium-subtitle">Ultimos avances en IA, Ciencia y Tecnologia</p>
    </div>

    <!-- Search and Filter Bar -->
    <div class="action-bar-container">
        <div class="action-bar">
            <form method="GET" class="search-form">
                <input type="text" name="q" placeholder="Buscar en biblioteca..." value="{{ search_query }}"
                    class="premium-input">
                <select name="category" class="premium-select" id="category-filter">
                    <option value="">Todas las Categorias</option>
                    {% for cat in categories %}
                    <option value="{{ cat.slug }}" {% if current_category == cat.slug %}selected{% endif %}>
                        {{ cat.name }}
                    </option>
                    {% endfor %}
                    <option disabled>----------</option>
                    <option value="_add">+ Anadir Categoria</option>
                    <option value="_delete">- Eliminar Categoria</option>
                </select>
                <button type="submit" class="premium-btn">Buscar</button>
            </form>

            <form method="POST" action="{% url 'researcher:news_refresh' %}">
                {% csrf_token %}
                <button type="submit" class="premium-btn refresh-btn">
                    <i class="fas fa-sync-alt"></i> Actualizar Hub
                </button>
                <a href="{% url 'researcher:source_list' %}" class="premium-btn sources-btn">
                    <i class="fas fa-list"></i> Fuentes
                </a>
            </form>
        </div>
    </div>

    {% if messages %}
    <div class="messages">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} animated-fade-in">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- News List -->
    <div class="news-grid" id="news-grid">
        {% for item in news_items %}
        {% include 'researcher/includes/news_card.html' with item=item %}
        {% empty %}
        <div class="empty-state">
            <p>No se encontraron noticias. Intenta actualizar o cambiar tu busqueda.</p>
        </div>
        {% endfor %}
    </div>

    <!-- Pagination -->
    {% if is_paginated %}
    <div class="pagination">
        <span class="step-links">
            {% if page_obj.has_previous %}
            <a href="?page=1&q={{ search_query }}&category={{ current_category }}" class="page-link">&laquo; primero</a>
            <a href="?page={{ page_obj.previous_page_number }}&q={{ search_query }}&category={{ current_category }}"
                class="page-link">anterior</a>
            {% endif %}

            <span class="current">
                Pagina {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
            </span>

            {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}&q={{ search_query }}&category={{ current_category }}"
                class="page-link">siguiente</a>
            <a href="?page={{ page_obj.paginator.num_pages }}&q={{ search_query }}&category={{ current_category }}"
                class="page-link">ultimo &raquo;</a>
            {% endif %}
        </span>
    </div>
    {% endif %}

    <!-- Modals for Category Management -->
    <div id="categoryModal" class="modal">
        <div class="modal-content">
            <h2 id="modalTitle">Anadir Categoria</h2>
            <div id="addCategoryForm">
                <input type="text" id="newCategoryName" class="premium-input" placeholder="Nombre de la categoria...">
                <div class="modal-actions">
                    <button class="premium-btn" onclick="saveCategory()">Guardar</button>
                    <button class="premium-btn cancel-btn" onclick="closeModal()">Cancelar</button>
                </div>
            </div>
            <div id="deleteCategoryForm" style="display:none;">
                <p>Selecciona una categoria para eliminar:</p>
                <select id="deleteCategorySelect" class="premium-select">
                    {% for cat in categories %}
                    <option value="{{ cat.id }}">{{ cat.name }}</option>
                    {% endfor %}
                </select>
                <div class="modal-actions">
                    <button class="premium-btn delete-confirm-btn" onclick="confirmDeleteCategory()">Eliminar</button>
                    <button class="premium-btn cancel-btn" onclick="closeModal()">Cancelar</button>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.8); backdrop-filter: blur(5px); }
    .modal-content { background: #1a1a1a; margin: 15% auto; padding: 2rem; border: 1px solid #333; width: 400px; border-radius: 15px; box-shadow: 0 0 30px rgba(0, 0, 0, 0.5); }
    .modal-content h2 { margin-top: 0; margin-bottom: 1.5rem; color: #fff; }
    .modal-actions { display: flex; gap: 1rem; margin-top: 1.5rem; }
    .cancel-btn { background: rgba(255, 255, 255, 0.1); }
    .delete-confirm-btn { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    #newCategoryName { width: 100%; margin-bottom: 1rem; }
    .research-container { padding: 2rem; max-width: 1200px; margin: 0 auto; }
    .header-section { text-align: center; margin-bottom: 3rem; }
    .premium-title { font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #a5a5a5 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }
    .premium-subtitle { color: #888; font-size: 1.2rem; }
    .action-bar { display: flex; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 15px; backdrop-filter: blur(10px); margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.1); }
    .search-form { display: flex; gap: 1rem; flex-grow: 1; }
    .action-bar-container { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; }
    .premium-input, .premium-select { background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.2); color: white; padding: 0.8rem 1.2rem; border-radius: 8px; outline: none; transition: border-color 0.3s; }
    .premium-input:focus, .premium-select:focus { border-color: #4facfe; }
    .premium-btn { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border: none; color: white; padding: 0.8rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
    .premium-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4); }
    .refresh-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin-right: 0.5rem; }
    .sources-btn { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem; }
    .messages { margin-bottom: 2rem; }
    .alert { padding: 1rem; border-radius: 8px; margin-bottom: 1rem; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); }
    .alert-success { border-color: #03dac6; color: #03dac6; }
    .alert-error { border-color: #cf6679; color: #cf6679; }
    .news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2rem; }
    .news-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 1.5rem; display: flex; flex-direction: column; transition: transform 0.3s, background 0.3s; }
    .news-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.05); }
    .card-header { display: flex; justify-content: space-between; margin-bottom: 1rem; }
    .category-badge { padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; text-transform: uppercase; font-weight: 700; }
    .category-badge.ai { background: rgba(79, 172, 254, 0.2); color: #4facfe; }
    .category-badge.science { background: rgba(67, 233, 123, 0.2); color: #43e97b; }
    .category-badge.tech { background: rgba(250, 112, 154, 0.2); color: #fa709a; }
    .impact-badge { font-size: 0.8rem; color: #888; }
    .news-card h3 { font-size: 1.4rem; line-height: 1.3; margin-bottom: 1rem; color: #eee; }
    .news-summary { color: #aaa; font-size: 0.95rem; line-height: 1.5; flex-grow: 1; margin-bottom: 1.5rem; }
    .card-footer { display: flex; justify-content: space-between; font-size: 0.85rem; color: #666; margin-bottom: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 1rem; }
    .card-actions { display: flex; gap: 1rem; align-items: center; }
    .text-link { color: #4facfe; text-decoration: none; font-size: 0.9rem; }
    .btn-create-script { background: rgba(255, 255, 255, 0.1); color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 0.9rem; transition: background 0.2s; }
    .btn-create-script:hover { background: rgba(255, 255, 255, 0.2); }
    .pagination { margin-top: 3rem; text-align: center; }
    .page-link { color: #4facfe; text-decoration: none; margin: 0 0.5rem; }
    .animated-fade-in { animation: fadeIn 0.5s ease-out forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .just-added-highlight { animation: highlightGlow 3s ease-out forwards; }
    @keyframes highlightGlow { 0% { box-shadow: 0 0 20px rgba(79, 172, 254, 0.8); border-color: #4facfe; transform: scale(1.02); } 100% { box-shadow: 0 0 0px rgba(79, 172, 254, 0); border-color: rgba(255, 255, 255, 0.05); transform: scale(1); } }
</style>

<script>
    document.addEventListener('DOMContentLoaded', function () {
        const refreshForm = document.querySelector('.refresh-btn')?.closest('form');
        const refreshBtn = document.querySelector('.refresh-btn');
        function showNotification(message, type = 'success') {
            const container = document.querySelector('.messages') || document.createElement('div');
            if (!container.classList.contains('messages')) {
                container.className = 'messages';
                const actionContainer = document.querySelector('.action-bar-container');
                if (actionContainer) actionContainer.after(container);
                else document.body.prepend(container);
            }
            const alert = document.createElement('div');
            alert.className = 'alert alert-' + (type === 'error' ? 'error' : 'success') + ' animated-fade-in';
            alert.textContent = message;
            container.appendChild(alert);
            setTimeout(() => { alert.style.opacity = '0'; setTimeout(() => alert.remove(), 500); }, 5000);
        }
        if (refreshForm) {
            refreshForm.addEventListener('submit', async function (e) {
                e.preventDefault();
                refreshBtn.disabled = true;
                const originalText = refreshBtn.innerHTML;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando...';
                try {
                    const response = await fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                    const data = await response.json();
                    showNotification(data.message, data.status);
                    if (data.status === 'success') setTimeout(() => window.location.reload(), 2000);
                } catch (error) { showNotification('Error al actualizar.', 'error'); }
                finally { refreshBtn.disabled = false; refreshBtn.innerHTML = originalText; }
            });
        }
        const categoryFilter = document.getElementById('category-filter');
        const categoryModal = document.getElementById('categoryModal');
        const addForm = document.getElementById('addCategoryForm');
        const deleteForm = document.getElementById('deleteCategoryForm');
        const modalTitle = document.getElementById('modalTitle');
        categoryFilter.addEventListener('change', function () {
            if (this.value === '_add') { modalTitle.textContent = 'Anadir Categoria'; addForm.style.display = 'block'; deleteForm.style.display = 'none'; categoryModal.style.display = 'block'; this.value = ''; }
            else if (this.value === '_delete') { modalTitle.textContent = 'Eliminar Categoria'; addForm.style.display = 'none'; deleteForm.style.display = 'block'; categoryModal.style.display = 'block'; this.value = ''; }
        });
        window.closeModal = () => { categoryModal.style.display = 'none'; };
        window.saveCategory = async () => {
            const name = document.getElementById('newCategoryName').value;
            if (!name) return;
            const response = await fetch('{% url "researcher:category_add" %}', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': '{{ csrf_token }}' }, body: 'name=' + encodeURIComponent(name) });
            const data = await response.json();
            if (data.status === 'success') window.location.reload(); else alert(data.message);
        };
        window.confirmDeleteCategory = async () => {
            const catId = document.getElementById('deleteCategorySelect').value;
            if (!catId) return;
            if (!confirm('Eliminar categoria?')) return;
            const response = await fetch('{% url "researcher:category_delete" %}', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': '{{ csrf_token }}' }, body: 'category_id=' + catId });
            const data = await response.json();
            if (data.status === 'success') window.location.reload(); else alert(data.message);
        };
    });
</script>
{% endblock %}
"""

target_path = r'c:\Users\Usuario\Documents\curso creacion contenido con ia\web_app2\web_app\researcher\templates\researcher\news_list.html'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully wrote UI to {target_path}")
