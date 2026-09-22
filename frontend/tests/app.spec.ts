import { test, expect } from '@playwright/test';

test.describe('NEXORA Dashboard Flows', () => {
  test('User Mode Navigation', async ({ page }) => {
    await page.goto('/');
    
    // Switch to User Mode
    await page.getByLabel('Research Mode').uncheck();
    
    // Ensure Research pages are hidden
    await expect(page.getByText('AI insights')).toBeHidden();
    await expect(page.getByText('Federated & privacy lab')).toBeHidden();
    await expect(page.getByText('Evidence')).toBeHidden();
    
    // Check available pages
    await expect(page.getByRole('link', { name: 'Participant' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
    
    // Start session
    await page.getByRole('button', { name: 'Start Session' }).click();
  });

  test('Comprehensive Research Mode Flow (20 steps)', async ({ page }) => {
    test.setTimeout(90000);

    // 1. Navigate to app
    await page.goto('/');
    
    // 2. Ensure we are in research mode
    await page.getByLabel('Research Mode').check();
    
    // 3. Go to Overview
    await page.getByRole('link', { name: 'Overview' }).click();
    
    // 4. Select Normal Scenario
    await page.getByRole('combobox').filter({ hasText: 'normal' }).selectOption('normal');
    
    // 5. Start normal session
    await page.getByRole('button', { name: 'Start synthetic session' }).click();

    // 6. Go to Live session
    await page.getByRole('link', { name: 'Live session' }).click();
    await expect(page.getByText('Model state')).toBeVisible();
    
    // 7. Pause session — navigate back to Overview and wait for Pause button
    await page.getByRole('link', { name: 'Overview' }).click();
    await page.getByRole('button', { name: 'Pause' }).waitFor({ state: 'visible', timeout: 15000 });
    await page.getByRole('button', { name: 'Pause' }).click();
    
    // 8. Resume session — wait for state transition before clicking Resume
    await page.getByRole('button', { name: 'Resume' }).waitFor({ state: 'visible', timeout: 15000 });
    await page.getByRole('button', { name: 'Resume' }).click();
    
    // 9. Stop session
    await page.getByRole('button', { name: 'Stop' }).waitFor({ state: 'visible', timeout: 15000 });
    await page.getByRole('button', { name: 'Stop' }).click();
    
    // 10. Select Missing Data scenario
    await page.getByRole('combobox').filter({ hasText: 'normal' }).selectOption('missing_data');
    
    // 11. Start missing data session
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    
    // 12. Verify missing data
    await page.getByRole('link', { name: 'Live session' }).click();
    await expect(page.getByText('Model state')).toBeVisible();
    
    // 13. Stop missing data session
    await page.getByRole('link', { name: 'Overview' }).click();
    await page.getByRole('button', { name: 'Stop' }).waitFor({ state: 'visible', timeout: 15000 });
    await page.getByRole('button', { name: 'Stop' }).click();
    
    // 14. Select Sustained Posture scenario (triggers intervention)
    await page.getByRole('combobox').filter({ hasText: 'missing_data' }).selectOption('sustained_posture');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    
    // 15. Wait a bit and check interventions
    await page.getByRole('link', { name: 'Interventions' }).click();
    
    // 16. Stop session
    await page.getByRole('link', { name: 'Overview' }).click();
    await page.getByRole('button', { name: 'Stop' }).waitFor({ state: 'visible', timeout: 15000 });
    await page.getByRole('button', { name: 'Stop' }).click();

    // 17. Federated & privacy lab
    await page.getByRole('link', { name: 'Federated & privacy lab' }).click();
    
    // 18. AI insights and explanation
    await page.getByRole('link', { name: 'AI insights' }).click();
    
    // 19. Check Settings & Privacy Projection
    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page.getByText('Privacy Budget Projections')).toBeVisible();

    // 20. Navigate to Evidence and Export
    await page.getByRole('link', { name: 'Evidence' }).click();
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Export Evidence JSON' }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe('evidence.json');
  });
});
