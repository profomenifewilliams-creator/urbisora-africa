# Urbisora Africa Ansible checks

Render is a managed platform, so Ansible should not attempt SSH provisioning of the Render container. Render deploys from GitHub; this playbook is for post-deploy HTTP smoke checks.

Run after the service deploys:

```bash
python -m pip install ansible
export URBISORA_URL=https://urbisora-africa.onrender.com
ansible-playbook -i localhost, ansible/verify-deployment.yml
```

The playbook checks the health endpoint, homepage and property search page. It retries cold starts and fails when a health check does not pass. Authenticated CRUD flows still require a separate functional test session.
