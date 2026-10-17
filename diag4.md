# Branch policy probe

## before
```json
{
  "total_count": 2,
  "branch_policies": [
    {
      "id": 63360825,
      "node_id": "MDE2OkdhdGVCcmFuY2hQb2xpY3k2MzM2MDgyNQ==",
      "name": "gas-turbine-generator-control",
      "type": "branch"
    },
    {
      "id": 63358664,
      "node_id": "MDE2OkdhdGVCcmFuY2hQb2xpY3k2MzM1ODY2NA==",
      "name": "gh-pages",
      "type": "branch"
    }
  ]
}

```

## add main
HTTP 403
```json
{
  "message": "Resource not accessible by integration",
  "documentation_url": "https://docs.github.com/rest/deployments/branch-policies#create-a-deployment-branch-policy",
  "status": "403"
}

```

## after
```json
{
  "total_count": 2,
  "branch_policies": [
    {
      "id": 63360825,
      "node_id": "MDE2OkdhdGVCcmFuY2hQb2xpY3k2MzM2MDgyNQ==",
      "name": "gas-turbine-generator-control",
      "type": "branch"
    },
    {
      "id": 63358664,
      "node_id": "MDE2OkdhdGVCcmFuY2hQb2xpY3k2MzM1ODY2NA==",
      "name": "gh-pages",
      "type": "branch"
    }
  ]
}

```
