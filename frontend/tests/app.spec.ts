import { test, expect } from '@playwright/test';

test.describe('NEXORA Dashboard Flows', () => {
  test('User Mode Navigation', async ({ page }) => {
    // Navigate to app
    await page.goto('/');
    
    // Switch to User Mode
    await page.getByLabel('Research Mode').uncheck();
    
    // Ensure Research pages are hidden
    await expect(page.getByText('AI insights')).toBeHidden();
    await expect(page.getByText('Federated & privacy lab')).toBeHidden();
    await expect(page.getByText('Evidence')).toBeHidden();
    
    // Check available pages
    await expect(page.getByRole('link', { name: 'Overview' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Live session' })).toBeVisible();
    
    // Start session
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    
    // Verify session started
    await expect(page.getByText('Active session ID:')).toBeVisible();
  });

  test('Research Mode Flow', async ({ page }) => {
    await page.goto('/');
    
    // Ensure we are in research mode
    await page.getByLabel('Research Mode').check();
    
    // Go to Overview first where the start button is
    await page.getByRole('link', { name: 'Overview' }).click();
    
    // Click Start
    await page.getByRole('button', { name: 'Start synthetic session' }).click();

    // Go to Live session
    await page.getByRole('link', { name: 'Live session' }).click();
    
    // Navigate to Evidence
    await page.getByRole('link', { name: 'Evidence' }).click();
    
    // Export Evidence
    page.on('dialog', dialog => dialog.accept());
    await page.getByRole('button', { name: 'Export Evidence ZIP' }).click();
  });
});
