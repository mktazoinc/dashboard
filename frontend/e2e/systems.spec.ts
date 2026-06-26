import { test, expect } from '@playwright/test';

test.describe('Sistemas do Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de autenticação para todos os testes
    await page.addInitScript(() => {
      window.localStorage.setItem('authToken', 'mock_token');
      window.localStorage.setItem('user', JSON.stringify({
        uid: 'test_user_123',
        email: 'test@example.com',
        role: 'admin'
      }));
    });
  });

  test.describe('Sistema 1 - Financeiro/Vendas', () => {
    test('deve acessar dashboard financeiro', async ({ page }) => {
      // Mock de dados financeiros
      await page.route('**/api/v1/finance/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user: 'test@example.com',
            role: 'comercial_rj',
            city: 'RJ',
            metrics: {
              total_receita: 1000000,
              total_despesa: 600000,
              lucro_liquido: 400000,
              margem_lucro: 40,
              vendas_mes: 800000,
              meta_mes: 1000000,
              perc_meta: 80,
              tickets_medio: 50000,
              total_vendas: 16,
              taxa_conversao: 25,
              receita_diaria: [
                { data: '2024-01-01', valor: 50000 },
                { data: '2024-01-02', valor: 75000 },
                { data: '2024-01-03', valor: 60000 }
              ],
              despesas_categoria: [
                { categoria: 'Marketing', valor: 150000 },
                { categoria: 'Operacional', valor: 250000 },
                { categoria: 'Pessoal', valor: 200000 }
              ],
              vendas_corretor: [
                { corretor: 'Pedro', vendas: 5, valor: 250000 },
                { corretor: 'Ana', vendas: 4, valor: 200000 },
                { corretor: 'Carlos', vendas: 3, valor: 150000 }
              ]
            }
          })
        });
      });

      await page.goto('/finance');
      
      // Verificar elementos do dashboard
      await expect(page.locator('h1')).toContainText('Sistema 1 - Financeiro/Vendas');
      await expect(page.locator('text=Receita Total')).toBeVisible();
      await expect(page.locator('text=Lucro Líquido')).toBeVisible();
      await expect(page.locator('text=Meta do Mês')).toBeVisible();
      
      // Verificar métricas
      await expect(page.locator('text=R$ 1.000.000')).toBeVisible();
      await expect(page.locator('text=R$ 400.000')).toBeVisible();
      await expect(page.locator('text=80%')).toBeVisible();
    });

    test('deve filtrar dados por período', async ({ page }) => {
      await page.route('**/api/v1/finance/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user: 'test@example.com',
            role: 'comercial_rj',
            metrics: { total_receita: 500000 }
          })
        });
      });

      await page.goto('/finance');
      
      // Selecionar período
      await page.click('button:has-text("Este mês")');
      await page.click('text=Últimos 30 dias');
      
      // Verificar se os dados foram atualizados
      await expect(page.locator('text=R$ 500.000')).toBeVisible();
    });
  });

  test.describe('Sistema 2 - Marketing', () => {
    test('deve acessar dashboard de marketing', async ({ page }) => {
      // Mock de dados de marketing
      await page.route('**/api/v1/marketing/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user: 'test@example.com',
            role: 'marketing_rj',
            city: 'RJ',
            metrics: {
              total_leads: 150,
              leads_em_atendimento: 45,
              visitas_agendadas: 30,
              vendas: 12,
              avg_cpl: 250,
              conversion_rate: 8,
              leads_by_status: {
                novo: 60,
                em_atendimento: 45,
                visita_agendada: 30,
                venda: 12,
                perdido: 3
              },
              leads_by_origem: {
                facebook: 50,
                google: 40,
                instagram: 30,
                indicacao: 20,
                outros: 10
              }
            }
          })
        });
      });

      await page.goto('/marketing');
      
      // Verificar elementos do dashboard
      await expect(page.locator('h1')).toContainText('Sistema 2 - Marketing');
      await expect(page.locator('text=Leads Totais')).toBeVisible();
      await expect(page.locator('text=Em Atendimento')).toBeVisible();
      await expect(page.locator('text=Visitas Agendadas')).toBeVisible();
      
      // Verificar métricas
      await expect(page.locator('text=150')).toBeVisible();
      await expect(page.locator('text=45')).toBeVisible();
      await expect(page.locator('text=R$ 250')).toBeVisible();
    });

    test('deve acessar tabela de leads', async ({ page }) => {
      // Mock de dados de leads
      await page.route('**/api/v1/marketing/leads', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            leads: [
              {
                id: 1,
                nome: 'João Silva',
                email: 'joao@example.com',
                telefone: '11999999999',
                status: 'novo',
                origem: 'facebook',
                data_entrada: '2024-01-15',
                corretor: 'Pedro'
              },
              {
                id: 2,
                nome: 'Maria Santos',
                email: 'maria@example.com',
                telefone: '11888888888',
                status: 'em_atendimento',
                origem: 'google',
                data_entrada: '2024-01-14',
                corretor: 'Ana'
              }
            ],
            total: 2,
            page: 1,
            page_size: 20,
            total_pages: 1
          })
        });
      });

      await page.goto('/marketing');
      
      // Clicar no link para ver todos os leads
      await page.click('a:has-text("Ver Todos os Leads")');
      
      // Verificar tabela de leads
      await expect(page).toHaveURL('/marketing/leads');
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('text=João Silva')).toBeVisible();
      await expect(page.locator('text=Maria Santos')).toBeVisible();
    });

    test('deve filtrar leads', async ({ page }) => {
      await page.route('**/api/v1/marketing/leads', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            leads: [
              {
                id: 1,
                nome: 'João Silva',
                status: 'novo',
                origem: 'facebook'
              }
            ],
            total: 1,
            page: 1,
            page_size: 20,
            total_pages: 1
          })
        });
      });

      await page.goto('/marketing/leads');
      
      // Aplicar filtros
      await page.fill('input[placeholder*="Buscar"]', 'João');
      await page.selectOption('select[name="status"]', 'novo');
      await page.selectOption('select[name="origem"]', 'facebook');
      
      // Verificar filtro aplicado
      await expect(page.locator('text=João Silva')).toBeVisible();
      await expect(page.locator('text=novo')).toBeVisible();
    });
  });

  test.describe('Sistema 3 - Admin', () => {
    test('deve acessar dashboard admin', async ({ page }) => {
      // Mock de dados admin
      await page.route('**/api/v1/admin/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user: 'test@example.com',
            role: 'admin',
            metrics: {
              total_users: 25,
              active_users: 20,
              logins_today: 15,
              logins_this_week: 80,
              systems_status: {
                finance: true,
                marketing: true,
                auth: true,
                cache: true,
                database: true
              },
              security_alerts: {
                failed_logins: 2,
                suspicious_activities: 0,
                blocked_ips: 1
              },
              performance: {
                avg_response_time: 150,
                cpu_usage: 45,
                memory_usage: 67,
                disk_usage: 78
              }
            },
            system_health: 'healthy'
          })
        });
      });

      await page.goto('/admin');
      
      // Verificar elementos do dashboard admin
      await expect(page.locator('h1')).toContainText('Sistema 3 - Admin');
      await expect(page.locator('text=Usuários Ativos')).toBeVisible();
      await expect(page.locator('text=Logins Hoje')).toBeVisible();
      await expect(page.locator('text=Status dos Sistemas')).toBeVisible();
      
      // Verificar métricas
      await expect(page.locator('text=20')).toBeVisible();
      await expect(page.locator('text=15')).toBeVisible();
      await expect(page.locator('text=Sistema Saudável')).toBeVisible();
    });

    test('deve navegar entre abas do admin', async ({ page }) => {
      await page.route('**/api/v1/admin/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user: 'test@example.com',
            role: 'admin',
            metrics: { total_users: 25 },
            system_health: 'healthy'
          })
        });
      });

      await page.goto('/admin');
      
      // Navegar para aba de usuários
      await page.click('button:has-text("Usuários")');
      await expect(page.locator('text=Gestão de Usuários')).toBeVisible();
      
      // Navegar para aba de segurança
      await page.click('button:has-text("Segurança")');
      await expect(page.locator('text=Segurança do Sistema')).toBeVisible();
      
      // Navegar para aba de sistema
      await page.click('button:has-text("Sistema")');
      await expect(page.locator('text=Informações do Sistema')).toBeVisible();
      
      // Voltar para visão geral
      await page.click('button:has-text("Visão Geral")');
      await expect(page.locator('text=Usuários Ativos')).toBeVisible();
    });
  });

  test.describe('Navegação entre Sistemas', () => {
    test('deve navegar entre sistemas usando menu', async ({ page }) => {
      // Mock para todos os sistemas
      await page.route('**/api/v1/finance/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: 'test@example.com', metrics: {} })
        });
      });

      await page.route('**/api/v1/marketing/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: 'test@example.com', metrics: {} })
        });
      });

      await page.route('**/api/v1/admin/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: 'test@example.com', metrics: {} })
        });
      });

      await page.goto('/dashboard');
      
      // Navegar para Sistema Financeiro
      await page.click('a:has-text("Sistema 1")');
      await expect(page).toHaveURL('/finance');
      await expect(page.locator('text=Sistema 1 - Financeiro/Vendas')).toBeVisible();
      
      // Navegar para Sistema Marketing
      await page.click('a:has-text("Sistema 2")');
      await expect(page).toHaveURL('/marketing');
      await expect(page.locator('text=Sistema 2 - Marketing')).toBeVisible();
      
      // Navegar para Sistema Admin
      await page.click('a:has-text("Sistema 3")');
      await expect(page).toHaveURL('/admin');
      await expect(page.locator('text=Sistema 3 - Admin')).toBeVisible();
    });

    test('deve manter navegação correta baseada em role', async ({ page }) => {
      // Mock para usuário com role marketing
      await page.addInitScript(() => {
        window.localStorage.setItem('authToken', 'mock_token');
        window.localStorage.setItem('user', JSON.stringify({
          uid: 'marketing_user_123',
          email: 'marketing@example.com',
          role: 'marketing_rj'
        }));
      });

      await page.route('**/api/v1/marketing/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: 'marketing@example.com', metrics: {} })
        });
      });

      await page.goto('/dashboard');
      
      // Usuário marketing deve ver link para Sistema Marketing
      await expect(page.locator('a:has-text("Sistema 2")')).toBeVisible();
      
      // Navegar para marketing
      await page.click('a:has-text("Sistema 2")');
      await expect(page).toHaveURL('/marketing');
      
      // Tentar acessar admin (deve ser bloqueado)
      await page.goto('/admin');
      await expect(page.locator('text=permissão')).toBeVisible();
    });
  });

  test.describe('Responsividade', () => {
    test('deve ser responsivo em mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone
      
      await page.route('**/api/v1/marketing/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: 'test@example.com', metrics: {} })
        });
      });

      await page.goto('/marketing');
      
      // Verificar layout mobile
      await expect(page.locator('h1')).toContainText('Sistema 2 - Marketing');
      
      // Menu deve estar colapsado/oculto em mobile
      await expect(page.locator('nav')).toHaveClass(/mobile/);
      
      // Cards devem empilhar verticalmente
      const cards = page.locator('.grid > div');
      const firstCard = cards.first();
      const firstCardBox = await firstCard.boundingBox();
      expect(firstCardBox?.width).toBeLessThan(400); // Largura menor em mobile
    });

    test('deve funcionar em tablet', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 }); // iPad
      
      await page.route('**/api/v1/finance/dashboard', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: 'test@example.com', metrics: {} })
        });
      });

      await page.goto('/finance');
      
      // Verificar layout tablet
      await expect(page.locator('h1')).toContainText('Sistema 1 - Financeiro/Vendas');
      
      // Grid deve ajustar para tablet
      const grid = page.locator('.grid');
      await expect(grid).toBeVisible();
    });
  });
});
