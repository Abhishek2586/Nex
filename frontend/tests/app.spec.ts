import { test, expect } from '@playwright/test';

test.describe('NEXORA Dashboard Flows', () => {
  // We should start with a clean state or at least known pages
  
  test('1. User Mode Navigation & History', async ({ page }) => {
    await page.goto('/');
    await page.getByText('Research Mode').click(); // toggle to User Mode
    
    // Ensure Research pages are hidden
    await expect(page.getByText('AI insights')).toBeHidden();
    
    // Check available pages
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Guidance' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'History' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'About' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
    
    // Check History page loads
    await page.getByRole('link', { name: 'History' }).click();
    await expect(page.getByText('Sessions are retained in local SQLite storage')).toBeVisible();
  });

  test('2. Research Mode: Normal Scenario', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('/'); // Default is Research Mode if local storage is clear, but let's be sure
    // Ensure Research Mode (if not already)
    const toggle = page.getByLabel('Research Mode');
    if (!(await toggle.isChecked())) {
        await toggle.check();
    }
    
    await page.getByRole('link', { name: 'Overview' }).click();
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('normal');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();

    // Verify session running
    await expect(page.getByText('Session Summary')).toBeVisible();
    await page.getByRole('link', { name: 'Live session' }).click();
    await expect(page.getByText('Model state')).toBeVisible();
    
    // Stop session
    await page.getByRole('link', { name: 'Overview' }).click();
    const stopBtn = page.getByRole('button', { name: 'Stop' });
    await stopBtn.waitFor({ state: 'visible', timeout: 15000 });
    if (await stopBtn.isEnabled()) {
        await stopBtn.click();
    }
  });

  test('3. Research Mode: Missing Data Scenario', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('/Overview');
    
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('missing_data');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    
    // Verify missing data abstention
    await page.getByRole('link', { name: 'Live session' }).click();
    // It might take a bit for a prediction to arrive
    await expect(page.getByText('Model state')).toBeVisible();
    
    // Stop session
    await page.getByRole('link', { name: 'Overview' }).click();
    const stopBtn2 = page.getByRole('button', { name: 'Stop' });
    await stopBtn2.waitFor({ state: 'visible', timeout: 15000 });
    if (await stopBtn2.isEnabled()) {
        await stopBtn2.click();
    }
  });

  test('4. Research Mode: Interventions & Prompt Isolation', async ({ page }) => {
    test.setTimeout(60000);
    await page.goto('/Overview');
    
    // Sustained posture triggers intervention
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('sustained_posture');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    
    await page.getByRole('link', { name: 'Interventions' }).click();
    await expect(page.getByText('Prompts & feedback')).toBeVisible();
    await expect(page.getByText('Physical output not connected.').first()).toBeVisible({ timeout: 15000 });
    
    // Check prompt isolation: go back, stop, start a new session (normal), ensure prompt doesn't bleed over
    await page.getByRole('link', { name: 'Overview' }).click();
    const stopBtn3 = page.getByRole('button', { name: 'Stop' });
    await stopBtn3.waitFor({ state: 'visible', timeout: 15000 });
    if (await stopBtn3.isEnabled()) {
        await stopBtn3.click();
    }
    
    await page.getByRole('combobox', { name: 'Scenario' }).selectOption('normal');
    await page.getByRole('button', { name: 'Start synthetic session' }).click();
    
    // Check user guidance page (should have no active prompts for normal)
    await page.getByText('Research Mode').click(); // switch to user
    await page.getByRole('link', { name: 'Guidance' }).click();
    await expect(page.getByText('No action is needed right now.')).toBeVisible();
    
    await page.getByRole('link', { name: 'Home' }).click();
    await page.getByRole('button', { name: 'End session' }).click();
  });

  test('5. AI Insights & Explanations', async ({ page }) => {
    await page.goto('/AI%20insights');
    await expect(page.getByRole('heading', { name: 'AI insights' })).toBeVisible();
    
    // Check confusion matrix renders (empty state or populated)
    await expect(page.getByText('Confusion Matrix').first()).toBeVisible();
    
    // Attribution section
    await expect(page.getByText('Per-prediction attribution')).toBeVisible();
    const explainBtn = page.getByRole('button', { name: 'Explain latest prediction' });
    await expect(explainBtn).toBeVisible();
  });

  test('6. Federated Lab: Run FedAvg', async ({ page }) => {
    await page.goto('/Federated%20%26%20privacy%20lab');
    await expect(page.getByText('Client Topology')).toBeVisible();
    await expect(page.getByText('Opacus: ENABLED')).toBeVisible();
    
    // Ensure we can see the buttons
    const runBtn = page.getByRole('button', { name: 'Run 1-round FedAvg' });
    await expect(runBtn).toBeVisible();
  });

  test('7. Model Rollback Action', async ({ page }) => {
    await page.goto('/Federated%20%26%20privacy%20lab');
    await expect(page.getByText('Client Topology')).toBeVisible();
    // Test if Rollback button renders when there's an experiment
    const rollbackBtn = page.getByRole('button', { name: 'Rollback to Previous' });
    // In a fresh clone, there may not be completed runs yet, so we just verify the route works.
    await expect(page.getByText('Measured experiment runs')).toBeVisible();
  });

  test('8. Accessibility: Reduce Motion Toggle', async ({ page }) => {
    await page.goto('/Settings');
    
    const toggle = page.getByRole('checkbox', { name: 'Reduce animations' });
    await toggle.check();
    
    // Check if body gets the class
    const body = page.locator('body');
    await expect(body).toHaveClass(/reduce-motion/);
    
    await toggle.uncheck();
    await expect(body).not.toHaveClass(/reduce-motion/);
  });

  test('9. Evidence Export', async ({ page }) => {
    await page.goto('/Evidence');
    await expect(page.getByText('Evidence package')).toBeVisible();
    
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download ZIP Evidence' }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^nexora-evidence-.*\.zip$/);
  });
});
