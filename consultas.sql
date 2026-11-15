-- 1. Livros mais emprestados
SELECT l.titulo, COUNT(*) AS total_emprestimos
FROM emprestimo e
JOIN exemplar ex ON ex.id = e.id_exemplar
JOIN livro l ON l.id = ex.id_livro
GROUP BY l.id, l.titulo
ORDER BY total_emprestimos DESC;

-- 2. Empréstimos em aberto e atrasados
SELECT s.nome, l.titulo, e.data_prevista,
       CAST(julianday('now') - julianday(e.data_prevista) AS INTEGER) AS dias_atraso
FROM emprestimo e
JOIN socio s ON s.id = e.id_socio
JOIN exemplar ex ON ex.id = e.id_exemplar
JOIN livro l ON l.id = ex.id_livro
WHERE e.data_devolucao IS NULL AND e.data_prevista < date('now')
ORDER BY dias_atraso DESC;

-- 3. Total de multas por sócio (e quanto está em aberto)
SELECT s.nome,
       SUM(m.valor) AS total_multas,
       SUM(CASE WHEN m.pago = 'nao' THEN m.valor ELSE 0 END) AS em_aberto
FROM multa m
JOIN emprestimo e ON e.id = m.id_emprestimo
JOIN socio s ON s.id = e.id_socio
GROUP BY s.id, s.nome
ORDER BY total_multas DESC;

-- 4. Empréstimos por categoria
SELECT c.genero, COUNT(*) AS total_emprestimos
FROM emprestimo e
JOIN exemplar ex ON ex.id = e.id_exemplar
JOIN livro l ON l.id = ex.id_livro
JOIN categoria c ON c.id = l.id_categoria
GROUP BY c.id, c.genero
ORDER BY total_emprestimos DESC;

-- 5. Empréstimos registrados por funcionário
SELECT f.nome, f.cargo, COUNT(*) AS emprestimos_registrados
FROM emprestimo e
JOIN funcionario f ON f.id = e.id_funcionario
GROUP BY f.id, f.nome, f.cargo
ORDER BY emprestimos_registrados DESC;
