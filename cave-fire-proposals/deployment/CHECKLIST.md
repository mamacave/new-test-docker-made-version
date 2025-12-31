# Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Code & Configuration
- [ ] All tests passing (`make e2e`, unit tests)
- [ ] Code reviewed and merged to main branch
- [ ] Version tagged (e.g., `v1.0.0`)
- [ ] Environment variables configured
- [ ] Secrets properly managed (not in code)
- [ ] Dependencies updated and locked

### Docker Image
- [ ] Dockerfile optimized
- [ ] `.dockerignore` configured
- [ ] Image built successfully
- [ ] Security scan passed (Trivy)
- [ ] Image pushed to registry
- [ ] Image size acceptable (<500MB recommended)

### Infrastructure
- [ ] Target environment prepared (cluster/cloud platform)
- [ ] Resource limits configured
- [ ] Networking configured (ingress, load balancer)
- [ ] SSL/TLS certificates ready
- [ ] DNS configured
- [ ] Monitoring/logging ready

### Kubernetes Specific
- [ ] Namespace created
- [ ] ConfigMaps/Secrets created
- [ ] Resource quotas set
- [ ] Network policies defined
- [ ] Pod Security Standards applied
- [ ] HPA configured
- [ ] PDB (Pod Disruption Budget) set
- [ ] Ingress controller ready

## Deployment

### Initial Deploy
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Verify health checks
- [ ] Check logs for errors
- [ ] Test all endpoints
- [ ] Performance test
- [ ] Load test (if applicable)

### Production Deploy
- [ ] Notify team of deployment
- [ ] Create backup/snapshot (if applicable)
- [ ] Deploy during low-traffic window
- [ ] Monitor deployment progress
- [ ] Verify pods/containers starting
- [ ] Check health endpoints
- [ ] Verify external access
- [ ] Run production smoke tests

## Post-Deployment

### Validation
- [ ] All endpoints responding correctly
- [ ] Response times acceptable
- [ ] No errors in logs
- [ ] Metrics collecting properly
- [ ] Alerts configured and working
- [ ] Documentation updated

### Monitoring (First 24h)
- [ ] Monitor error rates
- [ ] Watch resource usage (CPU/memory)
- [ ] Check response times
- [ ] Review logs for warnings
- [ ] Monitor pod restarts
- [ ] Verify auto-scaling works (if enabled)

### Rollback Plan
- [ ] Previous version available
- [ ] Rollback procedure documented
- [ ] Team aware of rollback process
- [ ] Database migration rollback ready (if applicable)

## Platform-Specific Checks

### Docker Compose
- [ ] All services started
- [ ] Nginx proxy working
- [ ] Volumes mounted correctly
- [ ] Networks configured
- [ ] Restart policies set

### Kubernetes
- [ ] All pods running
- [ ] Services created
- [ ] Ingress configured
- [ ] HPA active
- [ ] PDB enforced
- [ ] Resource limits applied

### Cloud Run
- [ ] Service deployed
- [ ] Custom domain mapped
- [ ] SSL certificate active
- [ ] Concurrency limits set
- [ ] Timeout configured

### ECS
- [ ] Task definition created
- [ ] Service running
- [ ] ALB/NLB configured
- [ ] Target group healthy
- [ ] Auto-scaling configured

## Security Checklist

- [ ] Running as non-root user
- [ ] No secrets in environment variables
- [ ] Network policies restricting traffic
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Input validation in place
- [ ] Dependencies vulnerability-free

## Disaster Recovery

- [ ] Backup strategy defined
- [ ] Recovery procedure documented
- [ ] Recovery time tested
- [ ] Data retention policy set
- [ ] Incident response plan ready

## Communication

- [ ] Deployment announcement sent
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Stakeholders notified
- [ ] Team trained on new features

---

## Quick Commands

**Check deployment status:**
```bash
# Docker
docker ps
docker logs cave-fire-proposals

# Kubernetes
kubectl get all -n cave-fire-proposals
kubectl logs -f -l app=cave-fire-proposals-api -n cave-fire-proposals

# Cloud Run
gcloud run services describe cave-fire-proposals
```

**Rollback:**
```bash
# Kubernetes
kubectl rollout undo deployment/cave-fire-proposals-api -n cave-fire-proposals

# Docker Compose
docker-compose down
# Update image tag in docker-compose.yml
docker-compose up -d
```

**Emergency stop:**
```bash
# Docker
docker stop cave-fire-proposals

# Kubernetes
kubectl scale deployment cave-fire-proposals-api --replicas=0 -n cave-fire-proposals

# Cloud Run
gcloud run services delete cave-fire-proposals
```
