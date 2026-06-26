import { test, expect } from '@playwright/test';

test.describe('Autenticação', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('deve exibir página de login', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard AZO');
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('deve mostrar erro com credenciais inválidas', async ({ page }) => {
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Esperar mensagem de erro
    await expect(page.locator('text=credenciais inválidas')).toBeVisible({ timeout: 10000 });
  });

  test('deve fazer login com sucesso e redirecionar para dashboard', async ({ page }) => {
    // Mock de resposta de login bem-sucedido
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock_token',
          token_type: 'bearer',
          user: {
            uid: 'test_user_123',
            email: 'test@example.com',
            role: 'admin'
          }
        })
      });
    });

    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpassword');
    await page.click('button[type="submit"]');

    // Esperar redirecionamento para dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Bem-vindo, test@example.com')).toBeVisible();
  });

  test('deve fazer logout corretamente', async ({ page }) => {
    // Mock de login
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock_token',
          token_type: 'bearer',
          user: {
            uid: 'test_user_123',
            email: 'test@example.com',
            role: 'admin'
          }
        })
      });
    });

    // Fazer login
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpassword');
    await page.click('button[type="submit"]');

    // Esperar redirecionamento
    await expect(page).toHaveURL('/dashboard');

    // Fazer logout
    await page.click('button:has-text("Sair")');

    // Verificar redirecionamento para login
    await expect(page).toHaveURL('/login');
  });

  test('deve proteger rotas autenticadas', async ({ page }) => {
    // Tentar acessar dashboard sem autenticação
    await page.goto('/dashboard');
    
    // Deve redirecionar para login
    await expect(page).toHaveURL('/login');
  });

  test('deve manter sessão ao recarregar página', async ({ page }) => {
    // Mock de login
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock_token',
          token_type: 'bearer',
          user: {
            uid: 'test_user_123',
            email: 'test@example.com',
            role: 'admin'
          }
        })
      });
    });

    // Fazer login
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpassword');
    await page.click('button[type="submit"]');

    // Esperar dashboard
    await expect(page).toHaveURL('/dashboard');

    // Recarregar página
    await page.reload();

    // Deve continuar logado
    await expect(page.locator('text=Bem-vindo, test@example.com')).toBeVisible();
  });
});
